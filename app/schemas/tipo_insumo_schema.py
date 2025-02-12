from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TipoInsumoBase(BaseModel):
    """Schema base para tipos de insumo como 'Tela', 'Riel', etc."""
    nombre: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Nombre del tipo de insumo, ej: 'Tela', 'Riel'"
    )
    descripcion: Optional[str] = Field(
        None, 
        max_length=500,
        description="Descripción detallada del tipo de insumo"
    )

class TipoInsumoCreate(TipoInsumoBase):
    """Schema para crear nuevos tipos de insumo"""
    pass

class TipoInsumoUpdate(BaseModel):
    """Schema para actualizar tipos de insumo existentes"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = None

class TipoInsumoInDB(TipoInsumoBase):
    """Schema para tipos de insumo como se almacenan en la base de datos"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True
