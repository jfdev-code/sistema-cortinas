# app/schemas/cotizacion_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal

class CotizacionInput(BaseModel):
    """
    Esquema para validar los datos de entrada de una cotización.
    Incluye validaciones específicas para cada campo.
    """
    diseno_id: int = Field(..., gt=0)
    ancho: float = Field(..., gt=20, le=500)
    alto: float = Field(..., gt=20, le=500)
    cantidad: int = Field(1, ge=1, le=100)
    factor_urgencia: float = Field(1.0, ge=1.0, le=2.0)
    descuento: Optional[float] = Field(None, ge=0, le=0.5)

    @validator('ancho', 'alto')
    def validar_dimensiones(cls, v):
        """Asegura que las dimensiones tengan máximo 2 decimales"""
        return round(v, 2)

    @validator('factor_urgencia')
    def validar_factor_urgencia(cls, v):
        """Asegura que el factor de urgencia tenga máximo 2 decimales"""
        return round(v, 2)

    @validator('descuento')
    def validar_descuento(cls, v):
        """Asegura que el descuento tenga máximo 2 decimales"""
        if v is not None:
            return round(v, 2)
        return v

    class Config:
        schema_extra = {
            "example": {
                "diseno_id": 1,
                "ancho": 150.5,
                "alto": 200.0,
                "cantidad": 2,
                "factor_urgencia": 1.2,
                "descuento": 0.1
            }
        }