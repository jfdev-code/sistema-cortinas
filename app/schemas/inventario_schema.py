from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MovimientoInventario(BaseModel):
    """Schema para registrar movimientos de inventario"""
    cantidad: float = Field(
        ...,
        description="Cantidad a agregar (positivo) o retirar (negativo)"
    )
    tipo_movimiento: str = Field(
        ...,
        description="Tipo de movimiento: 'entrada' o 'salida'"
    )
    motivo: Optional[str] = Field(
        None,
        max_length=500,
        description="Razón del movimiento de inventario"
    )

class InventarioInsumoBase(BaseModel):
    """
    Schema base para el inventario de insumos.
    Registra las cantidades disponibles de cada color de cada referencia.
    """
    referencia_id: int = Field(
        ...,
        description="ID de la referencia del insumo"
    )
    color_id: int = Field(
        ...,
        description="ID del color específico"
    )
    cantidad: float = Field(
        ..., 
        ge=0,
        description="Cantidad actual en inventario"
    )
    cantidad_minima: float = Field(
        ..., 
        ge=0,
        description="Cantidad mínima antes de generar alerta"
    )
    ubicacion: Optional[str] = Field(
        None, 
        max_length=100,
        description="Ubicación física del insumo en el almacén"
    )

class InventarioInsumoCreate(InventarioInsumoBase):
    """Schema para crear nuevos registros de inventario"""
    pass

class InventarioInsumoUpdate(BaseModel):
    """Schema para actualizar registros de inventario"""
    cantidad: Optional[float] = Field(None, ge=0)
    cantidad_minima: Optional[float] = Field(None, ge=0)
    ubicacion: Optional[str] = Field(None, max_length=100)

class InventarioInsumoInDB(InventarioInsumoBase):
    """Schema para registros de inventario como se almacenan en la base de datos"""
    id: int
    fecha_ultima_entrada: Optional[datetime]
    fecha_ultima_salida: Optional[datetime]
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True