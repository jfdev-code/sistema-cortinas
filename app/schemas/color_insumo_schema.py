from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ColorInsumoBase(BaseModel):
    """
    Schema base para colores de insumos.
    Cada referencia puede tener múltiples colores disponibles.
    """
    referencia_id: int = Field(
        ...,
        description="ID de la referencia a la que pertenece este color"
    )
    codigo: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="Código del color, ej: 'BLK-001-WHITE'"
    )
    nombre: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Nombre del color, ej: 'Blanco Perla'"
    )

class ColorInsumoCreate(ColorInsumoBase):
    """Schema para crear nuevos colores"""
    pass

class ColorInsumoUpdate(BaseModel):
    """Schema para actualizar colores existentes"""
    codigo: Optional[str] = Field(None, min_length=3, max_length=50)
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)

class ColorInsumoInDB(ColorInsumoBase):
    """Schema para colores como se almacenan en la base de datos"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True
