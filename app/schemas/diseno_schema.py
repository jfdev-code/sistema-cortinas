# app/schemas/diseno_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class DisenoTipoInsumoBase(BaseModel):
    """Base schema for the relationship between designs and supply types."""
    tipo_insumo_id: int = Field(..., description="ID of the required supply type")
    referencia_id: Optional[int] = Field(None, description="ID of the specific reference to use")
    color_id: Optional[int] = Field(None, description="ID of the specific color to use")
    cantidad_por_metro: float = Field(..., gt=0, description="Required quantity per meter of curtain width")
    descripcion: Optional[str] = Field(None, max_length=500, description="Notes about the use of this supply type")

    model_config = ConfigDict(from_attributes=True)

class DisenoBase(BaseModel):
    """Base schema for curtain designs."""
    id_diseno: str = Field(..., min_length=3, max_length=50, description="Unique design code, e.g., 'CORTINA-001'")
    nombre: str = Field(..., min_length=3, max_length=100, description="Descriptive name of the design")
    descripcion: Optional[str] = Field(None, max_length=500, description="Detailed description of the design")
    costo_mano_obra: float = Field(..., gt=0, description="Fixed labor cost for this design")
    complejidad: Optional[str] = Field('medio', description="Design complexity level: bajo, medio, alto")

    model_config = ConfigDict(from_attributes=True)

class DisenoCreate(DisenoBase):
    """Schema for creating new designs."""
    tipos_insumo: List[DisenoTipoInsumoBase] = Field(
        ...,
        min_items=1,
        description="List of required supply types and their quantities"
    )

class DisenoUpdate(BaseModel):
    """Schema for updating existing designs."""
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = None
    costo_mano_obra: Optional[float] = Field(None, gt=0)
    complejidad: Optional[str] = Field(None, pattern="^(bajo|medio|alto)$")
    tipos_insumo: Optional[List[DisenoTipoInsumoBase]] = None

    model_config = ConfigDict(from_attributes=True)

class DisenoInDB(DisenoBase):
    """Schema for designs as stored in the database."""
    id: int
    version: Optional[str]
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    tipos_insumo: List[DisenoTipoInsumoBase]

    model_config = ConfigDict(from_attributes=True)