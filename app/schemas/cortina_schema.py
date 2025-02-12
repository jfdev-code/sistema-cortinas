# app/schemas/cortina_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional
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
    Podría incluir campos adicionales específicos para la creación.
    """
    notas: Optional[str] = Field(None, max_length=500, description="Notas especiales para la fabricación")

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
    Incluye información calculada como el costo total y el área.
    """
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    estado: str
    notas: Optional[str]
    #area: float  # Calculado automáticamente
    costo_total: float  # Calculado basado en el diseño y las dimensiones

    class Config:
        orm_mode = True