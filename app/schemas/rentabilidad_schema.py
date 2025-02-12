# app/schemas/rentabilidad_schema.py
"""
Define los esquemas de datos para el análisis de rentabilidad.
Estos esquemas aseguran la validación de datos y documentación clara.
"""
from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal

class AnalisisRentabilidad(BaseModel):
    """
    Esquema que representa el análisis detallado de rentabilidad de una cortina.
    """
    cortina_id: int = Field(..., description="ID de la cortina analizada")
    rentabilidad_deseada: float = Field(
        ..., 
        gt=1.0,
        le=5.0,
        description="Factor de rentabilidad (ejemplo: 1.5 = 50% de ganancia)"
    )
    demanda_mensual: int = Field(
        ..., 
        gt=0,
        description="Cantidad esperada de ventas por mes"
    )
    costo_total: float = Field(
        None,
        description="Costo total de producción por unidad"
    )
    precio_sugerido: float = Field(
        None,
        description="Precio de venta sugerido para alcanzar la rentabilidad deseada"
    )
    margen_unitario: float = Field(
        None,
        description="Margen de ganancia por unidad vendida"
    )
    ingreso_mensual_proyectado: float = Field(
        None,
        description="Ingreso total mensual basado en la demanda esperada"
    )
    punto_equilibrio: int = Field(
        None,
        description="Cantidad mínima de ventas para cubrir costos"
    )
    rentabilidad_efectiva: float = Field(
        None,
        description="Rentabilidad real calculada"
    )

class ResultadoRentabilidad(BaseModel):
    """
    Esquema que representa el resultado completo del análisis de rentabilidad,
    incluyendo recomendaciones y clasificación.
    """
    analisis: AnalisisRentabilidad
    es_rentable: bool = Field(..., description="Indica si el proyecto es rentable")
    recomendaciones: List[str] = Field(..., description="Lista de recomendaciones basadas en el análisis")
    nivel_rentabilidad: str = Field(..., description="Clasificación de la rentabilidad: Alta, Media o Baja")

    class Config:
        schema_extra = {
            "example": {
                "analisis": {
                    "cortina_id": 1,
                    "rentabilidad_deseada": 1.5,
                    "demanda_mensual": 10,
                    "costo_total": 100000.0,
                    "precio_sugerido": 150000.0,
                    "margen_unitario": 50000.0,
                    "ingreso_mensual_proyectado": 1500000.0,
                    "punto_equilibrio": 8,
                    "rentabilidad_efectiva": 0.5
                },
                "es_rentable": True,
                "recomendaciones": [
                    "La demanda proyectada supera el punto de equilibrio",
                    "El margen de ganancia es saludable"
                ],
                "nivel_rentabilidad": "Alta"
            }
        }