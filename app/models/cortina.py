# app/models/cortina.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import expression

from . import Base  # Import Base from database module

class Cortina(Base):
    """
    Model representing a physical curtain with its dimensions and characteristics.
    This model tracks each curtain's measurements, costs, and production status.
    """
    __tablename__ = 'cortinas'

    # Primary key and relationships
    id = Column(Integer, primary_key=True, index=True)
    diseno_id = Column(Integer, ForeignKey('disenos.id', ondelete='CASCADE'), nullable=False)

    # Physical dimensions
    ancho = Column(Numeric(10, 2), nullable=False, comment='Width in centimeters')
    alto = Column(Numeric(10, 2), nullable=False, comment='Height in centimeters')
    
    # Configuration options
    partida = Column(Boolean, default=False, comment='Split curtain flag')
    multiplicador = Column(Integer, default=1, comment='Multiplier for multiple panels')
    
    # Financial and status tracking
    costo_total = Column(
        Numeric(10, 2), 
        nullable=False, 
        server_default=expression.text('0.0'),  # SQL-level default
        comment='Total cost calculated'
    )
    estado = Column(String(50), default='pendiente', comment='Current status')
    
    # Additional information
    notas = Column(Text, nullable=True, comment='Additional notes or specifications')
    
    # Timestamps for tracking
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )

    # Relationships
    diseno = relationship(
        "Diseno",
        back_populates="cortinas",
        lazy="joined"  # Use joined loading for better performance
    )

    def __repr__(self):
        """Provide a useful string representation of the curtain"""
        return (
            f"<Cortina(id={self.id}, "
            f"dimensiones={self.ancho}x{self.alto}cm, "
            f"estado='{self.estado}')>"
        )