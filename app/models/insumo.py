# # app/models/tipo_insumo.py
# from sqlalchemy import Column, Integer, String, DateTime
# from sqlalchemy.orm import relationship
# from datetime import datetime

# from .base_model import Base

# class TipoInsumo(Base):
#     """
#     Model representing general categories of supplies like 'Fabric', 'Rail', 'Accessories', etc.
#     This is a fundamental model that other models depend on.
#     """
#     __tablename__ = "tipos_insumo"
    
#     # Primary key
#     id = Column(Integer, primary_key=True, index=True)
    
#     # Basic fields
#     nombre = Column(String(100), nullable=False, unique=True)
#     descripcion = Column(String(500))
    
#     # Timestamps
#     fecha_creacion = Column(DateTime, default=datetime.utcnow)
#     fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships - using back_populates for better consistency
#     referencias = relationship(
#         "ReferenciaInsumo",
#         back_populates="tipo_insumo",
#         cascade="all, delete-orphan"
#     )
    
#     disenos = relationship(
#         "DisenoTipoInsumo",
#         back_populates="tipo_insumo",
#         cascade="all, delete-orphan"
#     )

#     def __repr__(self):
#         """Provide a useful string representation of the tipo insumo"""
#         return f"<TipoInsumo(id={self.id}, nombre='{self.nombre}')>"

#     def to_dict(self):
#         """Convert the model instance to a dictionary"""
#         return {
#             "id": self.id,
#             "nombre": self.nombre,
#             "descripcion": self.descripcion,
#             "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
#             "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
#         }