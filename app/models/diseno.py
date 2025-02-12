# app/models/diseno.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.schema import UniqueConstraint

from . import Base

class Diseno(Base):
    """Model that represents a curtain design template with its specifications."""
    __tablename__ = 'disenos'

    # Primary key and identification
    id = Column(Integer, primary_key=True, index=True)
    id_diseno = Column(String(50), unique=True, index=True, nullable=False)
    
    # Basic information
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Financial information
    costo_mano_obra = Column(Float, default=0.0, nullable=False)
    complejidad = Column(String(20), default='medio', nullable=False)  # bajo, medio, alto
    version = Column(String(20), nullable=True)
    
    # Relationships with explicit back_populates
    tipos_insumo = relationship(
        "DisenoTipoInsumo", 
        back_populates="diseno",
        cascade="all, delete-orphan"
    )
    cortinas = relationship(
        "Cortina",
        back_populates="diseno",
        cascade="all, delete-orphan"
    )

    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Diseno(id={self.id}, nombre='{self.nombre}')>"


class DisenoTipoInsumo(Base):
    """Model that represents the relationship between designs and supply types."""
    __tablename__ = 'diseno_tipos_insumo'

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys with explicit constraints
    diseno_id = Column(
        Integer, 
        ForeignKey('disenos.id', ondelete='CASCADE', name='fk_diseno_tipos_insumo_diseno_id'), 
        nullable=False,
        index=True
    )
    tipo_insumo_id = Column(
        Integer, 
        ForeignKey('tipos_insumo.id', ondelete='CASCADE', name='fk_diseno_tipos_insumo_tipo_insumo_id'), 
        nullable=False,
        index=True
    )
    referencia_id = Column(
        Integer, 
        ForeignKey('referencias_insumo.id', ondelete='SET NULL', name='fk_diseno_tipos_insumo_referencia_id'), 
        nullable=True
    )
    color_id = Column(
        Integer, 
        ForeignKey('colores_insumo.id', ondelete='SET NULL', name='fk_diseno_tipos_insumo_color_id'), 
        nullable=True
    )
    
    # Attributes
    cantidad_por_metro = Column(Float, nullable=False)
    descripcion = Column(Text, nullable=True)

    # Unique constraint to prevent duplicate entries
    __table_args__ = (
        UniqueConstraint('diseno_id', 'tipo_insumo_id', name='uq_diseno_tipos_insumo'),
    )

    # Relationships with explicit back_populates
    diseno = relationship(
        "Diseno", 
        back_populates="tipos_insumo",
        foreign_keys=[diseno_id]
    )
    tipo_insumo = relationship(
        "TipoInsumo", 
        back_populates="disenos",
        foreign_keys=[tipo_insumo_id]
    )
    referencia = relationship("ReferenciaInsumo")
    color = relationship("ColorInsumo")

    def __repr__(self):
        return f"<DisenoTipoInsumo(diseno_id={self.diseno_id}, tipo_insumo_id={self.tipo_insumo_id})>"