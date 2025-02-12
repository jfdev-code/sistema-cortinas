from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class InventarioInsumo(Base):
    
    """Modelo que gestiona el inventario de insumos por color"""
    __tablename__ = "inventario_insumos"

    id = Column(Integer, primary_key=True, index=True)
    referencia_id = Column(Integer, ForeignKey('referencias_insumo.id'), nullable=False)
    color_id = Column(Integer, ForeignKey('colores_insumo.id'), nullable=False)
    cantidad = Column(Float, nullable=False, default=0)
    cantidad_minima = Column(Float, nullable=False, default=0)
    ubicacion = Column(String(100))
    fecha_ultima_entrada = Column(DateTime)
    fecha_ultima_salida = Column(DateTime)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    referencia = relationship("ReferenciaInsumo", back_populates="inventarios")
    color = relationship("ColorInsumo", back_populates="inventarios")

    def __repr__(self):
        return f"<InventarioInsumo(id={self.id}, cantidad={self.cantidad})>"
