# app/services/pricing.py
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.diseno import Diseno
from ..models.cortina import Cortina
from ..utils.exceptions import CortinasException

class PricingCalculator:
    def __init__(self, db: Session):
        self.db = db
        # Definimos factores base para los cálculos
        self.factor_complejidad = {
            "bajo": Decimal("1.0"),
            "medio": Decimal("1.2"),
            "alto": Decimal("1.5")
        }
        self.margen_base = Decimal("0.3")  # 30% margen base
        
    async def _calcular_costos_base(
        self,
        diseno: Diseno,
        ancho: Decimal,
        alto: Decimal,
        cantidad: int
    ) -> Dict[str, Decimal]:
        """
        Calcula los costos base de materiales y mano de obra de manera detallada.
        Considera el área total, desperdicios y economías de escala.
        """
        area = (ancho * alto) / 10000  # Convertimos a metros cuadrados
        costos = {
            "materiales": Decimal("0"),
            "mano_obra": Decimal("0"),
            "overhead": Decimal("0")
        }
        
        # Calculamos costo de materiales incluyendo desperdicios
        factor_desperdicio = self._calcular_factor_desperdicio(area)
        for tipo_insumo in diseno.tipos_insumo:
            cantidad_necesaria = (
                tipo_insumo.cantidad_por_metro * 
                ancho / 100 * 
                factor_desperdicio
            )
            
            # Obtenemos el precio más reciente del insumo
            precio_unitario = tipo_insumo.referencia.precio_unitario
            
            costo_material = Decimal(str(
                cantidad_necesaria * precio_unitario * cantidad
            ))
            
            costos["materiales"] += costo_material
        
        # Calculamos costo de mano de obra con factor de complejidad
        costo_mo_base = Decimal(str(diseno.costo_mano_obra))
        factor_complejidad = self.factor_complejidad[diseno.complejidad]
        
        costos["mano_obra"] = (
            costo_mo_base * 
            factor_complejidad * 
            cantidad * 
            self._calcular_factor_cantidad(cantidad)
        )
        
        # Calculamos overhead (costos indirectos)
        costos["overhead"] = (
            (costos["materiales"] + costos["mano_obra"]) * 
            Decimal("0.15")  # 15% de overhead
        )
        
        return costos
    
    def _calcular_factor_tamano(self, area: Decimal) -> Decimal:
        """
        Calcula el factor de ajuste basado en el tamaño de la cortina.
        Cortinas más grandes tienen un factor menor por economía de escala.
        """
        if area < 2:  # Menos de 2m²
            return Decimal("1.2")  # 20% extra por tamaño pequeño
        elif area < 4:  # Entre 2m² y 4m²
            return Decimal("1.0")  # Factor normal
        else:  # Más de 4m²
            return Decimal("0.9")  # 10% descuento por tamaño grande
    
    def _calcular_factor_desperdicio(self, area: Decimal) -> Decimal:
        """
        Calcula el factor de desperdicio basado en el área.
        Áreas pequeñas tienen mayor desperdicio proporcional.
        """
        if area < 1:  # Menos de 1m²
            return Decimal("1.25")  # 25% de desperdicio
        elif area < 3:  # Entre 1m² y 3m²
            return Decimal("1.15")  # 15% de desperdicio
        else:  # Más de 3m²
            return Decimal("1.10")  # 10% de desperdicio
    
    def _calcular_factor_cantidad(self, cantidad: int) -> Decimal:
        """
        Calcula el factor de descuento por cantidad.
        Mayor cantidad implica menor costo unitario.
        """
        if cantidad < 3:
            return Decimal("1.0")
        elif cantidad < 5:
            return Decimal("0.95")  # 5% descuento
        elif cantidad < 10:
            return Decimal("0.90")  # 10% descuento
        else:
            return Decimal("0.85")  # 15% descuento
    
    def _calcular_margen(
        self,
        subtotal: Decimal,
        cantidad: int
    ) -> Decimal:
        """
        Calcula el margen de ganancia basado en el subtotal y cantidad.
        Ajusta el margen según volumen y valor total.
        """
        margen = self.margen_base
        
        # Ajuste por cantidad
        if cantidad >= 5:
            margen -= Decimal("0.05")  # Reducimos margen 5% por volumen
        
        # Ajuste por valor total
        valor_total = subtotal * cantidad
        if valor_total > 10000:
            margen -= Decimal("0.03")  # Reducimos margen 3% por valor alto
        
        return margen
    
    def _redondear_precio(self, precio: Decimal) -> Decimal:
        """
        Redondea el precio al siguiente múltiplo de 100 para precios más comerciales.
        """
        return (precio / 100).quantize(Decimal("1."), rounding=ROUND_HALF_UP) * 100
    
    def _generar_recomendaciones(
        self,
        costos: Dict[str, Decimal],
        subtotal: Decimal,
        precio_final: Decimal,
        area: Decimal
    ) -> List[str]:
        """
        Genera recomendaciones basadas en el análisis de costos y precios.
        """
        recomendaciones = []
        
        # Análisis de margen
        margen_efectivo = (precio_final - subtotal) / precio_final * 100
        if margen_efectivo < 25:
            recomendaciones.append(
                "El margen está por debajo del objetivo. Considerar ajuste de precio o "
                "reducción de costos."
            )
        
        # Análisis de costos
        costo_m2 = subtotal / area
        if costo_m2 > 1000:
            recomendaciones.append(
                "El costo por metro cuadrado es alto. Verificar posibilidad de "
                "optimizar uso de materiales."
            )
        
        # Análisis de composición de costos
        if costos["materiales"] > subtotal * Decimal("0.7"):
            recomendaciones.append(
                "Los materiales representan más del 70% del costo. Considerar "
                "negociación con proveedores o alternativas más económicas."
            )
        
        return recomendaciones