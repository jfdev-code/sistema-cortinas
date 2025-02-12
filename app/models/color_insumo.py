# app/models/color_insumo.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class ColorInsumo(Base):
    """
    Represents colors available for supply references.
    
    This model captures the color variations of supply items, 
    ensuring each color is linked to a specific reference 
    and can be tracked across inventory and designs.
    """
    __tablename__ = "colores_insumo"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key with enhanced configuration
    referencia_id = Column(
        Integer, 
        ForeignKey('referencias_insumo.id', 
                   ondelete='CASCADE',  # Cascade delete if reference is removed
                   name='fk_colores_insumo_referencia_id'  # Named constraint
        ), 
        nullable=False,
        index=True  # Add index for performance
    )
    
    # Color-specific attributes
    codigo = Column(
        String(50), 
        nullable=False, 
        unique=True  # Ensure unique color codes
    )
    nombre = Column(
        String(100), 
        nullable=False, 
        index=True  # Add index for potential name-based searches
    )
    
    # Timestamp columns with more robust datetime handling
    fecha_creacion = Column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    fecha_actualizacion = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships with enhanced configuration
    referencia = relationship(
        "ReferenciaInsumo", 
        back_populates="colores",
        lazy="joined"  # Eager loading for better performance
    )
    
    inventarios = relationship(
        "InventarioInsumo", 
        back_populates="color",
        cascade="all, delete-orphan"  # Manage lifecycle of related inventory items
    )
    
    # Add relationship for design type associations
    diseno_tipos_insumo = relationship(
        "DisenoTipoInsumo", 
        back_populates="color",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """
        Provides a clear string representation of the color.
        Useful for debugging and logging.
        """
        return f"<ColorInsumo(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"

    def to_dict(self):
        """
        Converts the model instance to a dictionary.
        Useful for serialization and API responses.
        """
        return {
            "id": self.id,
            "referencia_id": self.referencia_id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }