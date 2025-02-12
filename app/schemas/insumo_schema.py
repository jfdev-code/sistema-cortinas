# # app/schemas/insumo_schema.py
# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import Optional

# class InsumoBase(BaseModel):
#     """
#     Esquema base para los datos comunes de un insumo.
#     Field nos permite agregar validaciones y descripciones a nuestros campos.
#     """
#     nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del insumo")
#     precio_unitario: float = Field(..., gt=0, description="Precio por unidad del insumo")
#     tipo_unidad: str = Field(..., description="Tipo de unidad (METRO o UNIDAD)")
#     iva: float = Field(default=0.16, ge=0, le=1, description="Tasa de IVA aplicable")

# class InsumoCreate(InsumoBase):
#     """
#     Esquema para crear un nuevo insumo.
#     Hereda de InsumoBase pero podría tener campos adicionales específicos para la creación.
#     """
#     # pass

# class InsumoUpdate(BaseModel):
#     """
#     Esquema para actualizar un insumo.
#     Todos los campos son opcionales porque podríamos querer actualizar solo algunos.
#     """
#     nombre: Optional[str] = Field(None, min_length=3, max_length=100)
#     precio_unitario: Optional[float] = Field(None, gt=0)
#     tipo_unidad: Optional[str] = None
#     iva: Optional[float] = Field(None, ge=0, le=1)

# class InsumoInDB(InsumoBase):
#     """
#     Esquema que representa cómo se ve un insumo cuando lo leemos de la base de datos.
#     Incluye campos adicionales que el sistema genera automáticamente.
#     """
#     id: int
#     fecha_creacion: datetime
#     fecha_actualizacion: datetime

#     class Config:
#         """
#         Esta configuración permite que Pydantic lea los objetos de la base de datos.
#         """
#         orm_mode = True