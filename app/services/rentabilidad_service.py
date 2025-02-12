# app/services/rentabilidad_service.py
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict

from ..models.cortina import Cortina
from ..schemas.rentabilidad_schema import ResultadoRentabilidad

async def calcular_precio_venta(
    db: AsyncSession,
    cortina_id: int,
    rentabilidad_deseada: float
) -> Dict:
    """
    Calcula el precio de venta necesario para alcanzar la rentabilidad deseada.
    
    Por ejemplo, si una cortina cuesta $100,000 producirla y queremos una rentabilidad
    del 30% (rentabilidad_deseada = 0.30), el precio de venta debería ser $130,000.
    
    Args:
        db: Sesión de base de datos asíncrona
        cortina_id: ID de la cortina a analizar
        rentabilidad_deseada: Porcentaje de rentabilidad deseada (0.30 = 30%)
    
    Returns:
        ResultadoRentabilidad con el análisis detallado
    """
    # Obtenemos la cortina y su costo de producción
    stmt = select(Cortina).where(Cortina.id == cortina_id)
    result = await db.execute(stmt)
    cortina = result.scalar_one_or_none()
    
    if not cortina:
        raise ValueError("Cortina no encontrada")

    # Costo de producción (viene de los insumos y cálculos previos)
    costo_produccion = float(cortina.costo_total)
    
    # Calculamos el precio de venta necesario para la rentabilidad deseada
    # Fórmula: precio_venta = costo_produccion * (1 + rentabilidad_deseada)
    precio_venta_sugerido = costo_produccion * (1 + rentabilidad_deseada)
    
    # Calculamos el margen de ganancia en pesos
    margen_ganancia = precio_venta_sugerido - costo_produccion
    
    # Preparamos un análisis detallado
    analisis = {
        "costo_produccion": round(costo_produccion, 2),
        "rentabilidad_solicitada": f"{rentabilidad_deseada * 100}%",
        "precio_venta_sugerido": round(precio_venta_sugerido, 2),
        "margen_ganancia": round(margen_ganancia, 2),
        "desglose_costos": {
            "materiales": "Desglose de costos de materiales por metro",
            "mano_obra": "Costo de mano de obra",
            "otros_costos": "Otros costos asociados"
        },
        "recomendaciones": []
    }
    
    # Agregamos recomendaciones basadas en el análisis
    if rentabilidad_deseada < 0.20:
        analisis["recomendaciones"].append(
            "La rentabilidad deseada está por debajo del 20%, "
            "considere aumentarla para mantener un margen saludable"
        )
    elif rentabilidad_deseada > 0.50:
        analisis["recomendaciones"].append(
            "La rentabilidad deseada es alta, asegúrese de que el mercado "
            "pueda absorber este precio"
        )
    
    # Comparamos con precios del mercado
    analisis["recomendaciones"].append(
        f"El precio sugerido de ${precio_venta_sugerido:,.2f} permite alcanzar "
        f"la rentabilidad deseada del {rentabilidad_deseada * 100}%"
    )
    
    return analisis