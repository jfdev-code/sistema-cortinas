# app/models/reserva_inventario.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from . import Base

class ReservaInventario(Base):
    """Modelo para manejar reservas temporales de inventario"""
    __tablename__ = "reservas_inventario"
    
    id = Column(Integer, primary_key=True, index=True)
    inventario_id = Column(Integer, ForeignKey('inventario_insumos.id'), nullable=False)
    cantidad = Column(Float, nullable=False)
    token = Column(String(50), unique=True, nullable=False, index=True)
    fecha_reserva = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime, nullable=False)
    estado = Column(String(20), default='activa')  # activa, utilizada, expirada
    
    # Índice compuesto para búsquedas eficientes
    __table_args__ = (
        Index('idx_reservas_estado_fecha', 'estado', 'fecha_expiracion'),
    )

# app/services/inventory_manager.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.reserva_inventario import ReservaInventario
from ..models.inventario_insumo import InventarioInsumo

class InventoryManager:
    def __init__(self, db: Session):
        self.db = db
    
    async def reservar_stock(
        self,
        items: Dict[int, float],  # Dict[inventario_id, cantidad]
        duracion_minutos: int = 15
    ) -> str:
        """
        Reserva stock temporalmente para una operación
        Retorna un token único para la reserva
        """
        token = str(uuid.uuid4())
        expiracion = datetime.utcnow() + timedelta(minutes=duracion_minutos)
        
        # Verificamos disponibilidad real
        for inv_id, cantidad in items.items():
            inventario = self.db.query(InventarioInsumo).filter(
                InventarioInsumo.id == inv_id
            ).with_for_update().first()
            
            if not inventario:
                raise ValueError(f"Inventario {inv_id} no encontrado")
            
            # Calculamos stock disponible real
            stock_reservado = self.db.query(ReservaInventario).filter(
                and_(
                    ReservaInventario.inventario_id == inv_id,
                    ReservaInventario.estado == 'activa',
                    ReservaInventario.fecha_expiracion > datetime.utcnow()
                )
            ).with_for_update().all()
            
            total_reservado = sum(r.cantidad for r in stock_reservado)
            disponible = inventario.cantidad - total_reservado
            
            if disponible < cantidad:
                raise ValueError(
                    f"Stock insuficiente para el item {inventario.id}. "
                    f"Disponible: {disponible}, Solicitado: {cantidad}"
                )
            
            # Creamos la reserva
            reserva = ReservaInventario(
                inventario_id=inv_id,
                cantidad=cantidad,
                token=token,
                fecha_expiracion=expiracion
            )
            self.db.add(reserva)
        
        self.db.commit()
        return token
    
    async def confirmar_reserva(self, token: str) -> None:
        """
        Confirma una reserva y actualiza el inventario real
        """
        reservas = self.db.query(ReservaInventario).filter(
            and_(
                ReservaInventario.token == token,
                ReservaInventario.estado == 'activa'
            )
        ).with_for_update().all()
        
        if not reservas:
            raise ValueError("Reserva no encontrada o ya expirada")
            
        for reserva in reservas:
            inventario = self.db.query(InventarioInsumo).filter(
                InventarioInsumo.id == reserva.inventario_id
            ).with_for_update().first()
            
            inventario.cantidad -= reserva.cantidad
            reserva.estado = 'utilizada'
        
        self.db.commit()
    
    async def liberar_reserva(self, token: str) -> None:
        """
        Libera una reserva sin afectar el inventario
        """
        reservas = self.db.query(ReservaInventario).filter(
            and_(
                ReservaInventario.token == token,
                ReservaInventario.estado == 'activa'
            )
        ).all()
        
        for reserva in reservas:
            reserva.estado = 'expirada'
        
        self.db.commit()
    
    async def limpiar_reservas_expiradas(self) -> int:
        """
        Limpia las reservas expiradas de la base de datos
        Retorna el número de reservas limpiadas
        """
        reservas_expiradas = self.db.query(ReservaInventario).filter(
            and_(
                ReservaInventario.estado == 'activa',
                ReservaInventario.fecha_expiracion <= datetime.utcnow()
            )
        ).all()
        
        for reserva in reservas_expiradas:
            reserva.estado = 'expirada'
        
        self.db.commit()
        return len(reservas_expiradas)