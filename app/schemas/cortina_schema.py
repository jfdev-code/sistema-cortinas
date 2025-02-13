# app/schemas/cortina_schema.py
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional
from datetime import datetime
from decimal import Decimal

class CortinaBase(BaseModel):
    """
    Esta clase define los atributos básicos que toda cortina debe tener.
    Usamos validadores para asegurar que las dimensiones sean razonables
    y que los cálculos sean precisos.
    """
    diseno_id: int = Field(..., description="ID del diseño de cortina a utilizar")
    ancho: float = Field(..., gt=0, le=500, description="Ancho de la cortina en centímetros")
    alto: float = Field(..., gt=0, le=500, description="Alto de la cortina en centímetros")
    partida: bool = Field(False, description="Indica si la cortina está dividida en el medio")
    multiplicador: int = Field(1, ge=1, le=10, description="Factor multiplicador para cortinas múltiples")

    @validator('ancho', 'alto')
    def validar_dimensiones(cls, v):
        """
        Asegura que las dimensiones sean razonables para una cortina.
        Por ejemplo, una cortina de 0.1cm sería demasiado pequeña.
        """
        if v < 20:  # 20 cm como mínimo razonable
            raise ValueError("La dimensión debe ser al menos 20 cm")
        return float(Decimal(str(v)).quantize(Decimal('.01')))  # Redondea a 2 decimales

class CortinaCreate(CortinaBase):
    """
    Esquema usado cuando se crea una nueva cortina.
    """
    diseno_id: int
    ancho: float
    alto: float
    partida: bool = False
    multiplicador: int = 1
    tipos_insumo: List[Dict[str, Any]]  # Lista de materiales seleccionados
    notas: Optional[str] = None

    @validator('ancho', 'alto')
    def validar_dimensiones(cls, v):
        """Asegura que las dimensiones sean razonables"""
        if v < 20 or v > 500:
            raise ValueError("Las dimensiones deben estar entre 20 y 500 cm")
        return float(v)

    @validator('multiplicador')
    def validar_multiplicador(cls, v):
        """Asegura que el multiplicador sea razonable"""
        if v < 1 or v > 10:
            raise ValueError("El multiplicador debe estar entre 1 y 10")
        return v

class CortinaUpdate(BaseModel):
    """
    Esquema para actualizar una cortina existente.
    Todos los campos son opcionales porque podríamos querer actualizar solo algunos.
    """
    ancho: Optional[float] = Field(None, gt=0, le=500)
    alto: Optional[float] = Field(None, gt=0, le=500)
    partida: Optional[bool] = None
    multiplicador: Optional[int] = Field(None, ge=1, le=10)
    notas: Optional[str] = Field(None, max_length=500)
    estado: Optional[str] = Field(None, description="Estado de la cortina")

class CortinaInDB(CortinaBase):
    """
    Esquema que representa cómo se ve una cortina cuando la leemos de la base de datos.
    """
    id: int
    diseno_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    estado: str
    notas: Optional[str]
    costo_materiales: float
    costo_mano_obra: float
    costo_total: float

    class Config:
        orm_mode = True