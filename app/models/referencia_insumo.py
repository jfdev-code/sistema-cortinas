# app/models/referencia_insumo.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base

class ReferenciaInsumo(Base):
    """
    Model representing specific references of supplies.
    For example, a type might be 'Fabric', and a reference would be 'Premium Blackout'.
    """
    __tablename__ = "referencias_insumo"
    # Add extend_existing to handle multiple imports gracefully
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to TipoInsumo
    tipo_insumo_id = Column(
        Integer, 
        ForeignKey('tipos_insumo.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Basic fields
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    precio_unitario = Column(Float, nullable=False)
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(
        DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    tipo_insumo = relationship(
        "TipoInsumo",
        back_populates="referencias",
        lazy="joined"  # Eager loading for better performance
    )
    
    colores = relationship(
        "ColorInsumo",
        back_populates="referencia",
        cascade="all, delete-orphan"
    )
    
    inventarios = relationship(
        "InventarioInsumo",
        back_populates="referencia",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """Provide a useful string representation"""
        return f"<ReferenciaInsumo(id={self.id}, codigo='{self.codigo}')>"

    def to_dict(self):
        """Convert the model instance to a dictionary"""
        return {
            "id": self.id,
            "tipo_insumo_id": self.tipo_insumo_id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "precio_unitario": self.precio_unitario,
            "tipo_insumo": self.tipo_insumo.nombre if self.tipo_insumo else None,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a new instance from a dictionary"""
        return cls(
            tipo_insumo_id=data.get('tipo_insumo_id'),
            codigo=data.get('codigo'),
            nombre=data.get('nombre'),
            precio_unitario=data.get('precio_unitario')
        )

    def update_from_dict(self, data: dict):
        """Update instance from a dictionary"""
        if 'codigo' in data:
            self.codigo = data['codigo']
        if 'nombre' in data:
            self.nombre = data['nombre']
        if 'precio_unitario' in data:
            self.precio_unitario = data['precio_unitario']
        # tipo_insumo_id is typically not updated after creation
        self.fecha_actualizacion = datetime.utcnow()