from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ReferenciaInsumoBase(BaseModel):
    """
    Schema base para referencias de insumos.
    Una referencia es una variante específica de un tipo de insumo,
    por ejemplo: 'Tela Blackout', 'Riel de Aluminio', etc.
    """
    tipo_insumo_id: int = Field(
        ...,
        description="ID del tipo de insumo al que pertenece esta referencia"
    )
    codigo: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="Código único de la referencia, ej: 'BLK-001'"
    )
    nombre: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Nombre descriptivo de la referencia"
    )
    precio_unitario: float = Field(
        ..., 
        gt=0,
        description="Precio por unidad de medida (metro, unidad, etc.)"
    )

class ReferenciaInsumoCreate(ReferenciaInsumoBase):
    """Schema para crear nuevas referencias de insumo"""
    pass

class ReferenciaInsumoUpdate(BaseModel):
    """Schema para actualizar referencias existentes"""
    codigo: Optional[str] = Field(None, min_length=3, max_length=50)
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    precio_unitario: Optional[float] = Field(None, gt=0)

class ReferenciaInsumoInDB(ReferenciaInsumoBase):
    """Schema para referencias como se almacenan en la base de datos"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True