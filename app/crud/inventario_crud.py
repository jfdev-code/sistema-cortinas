# app/crud/inventario_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timedelta

from ..models.inventario_insumo import InventarioInsumo
from ..models.referencia_insumo import ReferenciaInsumo
from ..models.color_insumo import ColorInsumo
from ..schemas.inventario_schema import (
    InventarioInsumoCreate,
    InventarioInsumoUpdate,
    MovimientoInventario
)
from ..utils.transaction import transaction_scope

async def create_inventario(db: AsyncSession, inventario: InventarioInsumoCreate) -> InventarioInsumo:
    """
    Create a new inventory record for a specific supply.
    """
    async with transaction_scope(db) as tx:
        # Check if record already exists
        existing = await get_inventario_by_color_ref(
            tx,
            referencia_id=inventario.referencia_id,
            color_id=inventario.color_id
        )
        
        if existing:
            raise ValueError(
                "Ya existe un registro de inventario para esta combinación de referencia y color"
            )
        
        # Create new inventory record
        db_inventario = InventarioInsumo(
            referencia_id=inventario.referencia_id,
            color_id=inventario.color_id,
            cantidad=inventario.cantidad,
            cantidad_minima=inventario.cantidad_minima,
            ubicacion=inventario.ubicacion,
            fecha_ultima_entrada=datetime.utcnow() if inventario.cantidad > 0 else None
        )
        
        tx.add(db_inventario)
        await tx.flush()
        
        return db_inventario

async def get_inventario(db: AsyncSession, inventario_id: int) -> Optional[InventarioInsumo]:
    """
    Get an inventory record by its ID.
    """
    stmt = select(InventarioInsumo).where(InventarioInsumo.id == inventario_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_inventario_by_color_ref(
    db: AsyncSession,
    referencia_id: int,
    color_id: int
) -> Optional[InventarioInsumo]:
    """
    Get inventory record for a specific reference and color combination.
    """
    stmt = select(InventarioInsumo).where(
        and_(
            InventarioInsumo.referencia_id == referencia_id,
            InventarioInsumo.color_id == color_id
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_inventario(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    solo_bajo_minimo: bool = False,
    tipo_insumo_id: Optional[int] = None
) -> List[InventarioInsumo]:
    """
    Get all inventory records with filtering options.
    """
    query = select(InventarioInsumo)
    
    if solo_bajo_minimo:
        query = query.where(InventarioInsumo.cantidad <= InventarioInsumo.cantidad_minima)
    
    if tipo_insumo_id:
        # Join with Referencia Insumo to filter by tipo_insumo
        query = (
            query
            .join(ReferenciaInsumo)
            .where(ReferenciaInsumo.tipo_insumo_id == tipo_insumo_id)
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_stock(
    db: AsyncSession,
    inventario_id: int,
    movimiento: MovimientoInventario
) -> Tuple[InventarioInsumo, bool]:
    """
    Update stock for an item and record the movement.
    """
    async with transaction_scope(db) as tx:
        # Find the inventory record
        stmt = select(InventarioInsumo).where(InventarioInsumo.id == inventario_id)
        result = await tx.execute(stmt)
        db_inv = result.scalar_one_or_none()
        
        if not db_inv:
            raise ValueError("Registro de inventario no encontrado")

        cantidad_delta = movimiento.cantidad
        if movimiento.tipo_movimiento == "sal ida":
            cantidad_delta = -cantidad_delta
            if db_inv.cantidad + cantidad_delta < 0:
                raise ValueError("Stock insuficiente para realizar la salida")

        db_inv.cantidad += cantidad_delta
        
        # Update timestamps based on movement type
        if cantidad_delta > 0:
            db_inv.fecha_ultima_entrada = datetime.utcnow()
        else:
            db_inv.fecha_ultima_salida = datetime.utcnow()
        
        db_inv.fecha_actualizacion = datetime.utcnow()
        
        return db_inv, db_inv.cantidad <= db_inv.cantidad_minima

async def verificar_disponibilidad(
    db: AsyncSession,
    referencia_id: int,
    color_id: int,
    cantidad_requerida: float
) -> bool:
    """
    Verify if there's enough stock available for a required quantity.
    """
    inventario = await get_inventario_by_color_ref(db, referencia_id, color_id)
    return inventario is not None and inventario.cantidad >= cantidad_requerida

async def get_alertas_stock(db: AsyncSession) -> List[Dict]:
    """
    Get a list of all items that require attention in inventory.
    """
    stmt = select(InventarioInsumo)
    result = await db.execute(stmt)
    inventarios = result.scalars().all()
    
    alertas = []
    fecha_limite = datetime.utcnow() - timedelta(days=30)
    
    for inv in inventarios:
        # Check low stock level
        if inv.cantidad <= inv.cantidad_minima:
            alertas.append({
                "tipo": "nivel_bajo",
                "inventario_id": inv.id,
                "referencia_id": inv.referencia_id,
                "color_id": inv.color_id,
                "cantidad_actual": inv.cantidad,
                "cantidad_minima": inv.cantidad_minima,
                "mensaje": f"Stock bajo: {inv.cantidad} unidades (mínimo: {inv.cantidad_minima})"
            })
        
        # Check inactivity
        ultima_actividad = max(
            inv.fecha_ultima_entrada or datetime.min,
            inv.fecha_ultima_salida or datetime.min
        )
        
        if ultima_actividad < fecha_limite:
            alertas.append({
                "tipo": "inactividad",
                "inventario_id": inv.id,
                "referencia_id": inv.referencia_id,
                "color_id": inv.color_id,
                "ultima_actividad": ultima_actividad,
                "mensaje": "Sin movimientos en los últimos 30 días"
            })
    
    return alertas

async def actualizar_inventario(
    db: AsyncSession,
    inventario_id: int,
    datos: InventarioInsumoUpdate
) -> Optional[InventarioInsumo]:
    """
    Update inventory record information.
    """
    async with transaction_scope(db) as tx:
        # Find the inventory record
        stmt = select(InventarioInsumo).where(InventarioInsumo.id == inventario_id)
        result = await tx.execute(stmt)
        db_inv = result.scalar_one_or_none()
        
        if not db_inv:
            return None
            
        # Update only provided fields
        update_data = datos.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_inv, field, value)
        
        db_inv.fecha_actualizacion = datetime.utcnow()
        
        return db_inv

async def delete_inventario(db: AsyncSession, inventario_id: int) -> bool:
    """
    Delete an inventory record.
    Only allowed if quantity is 0 to prevent data loss.
    """
    async with transaction_scope(db) as tx:
        # Find the inventory record
        stmt = select(InventarioInsumo).where(InventarioInsumo.id == inventario_id)
        result = await tx.execute(stmt)
        db_inv = result.scalar_one_or_none()
        
        if not db_inv:
            return False
            
        if db_inv.cantidad > 0:
            raise ValueError(
                "No se puede eliminar un registro de inventario con stock disponible"
            )
        
        await tx.delete(db_inv)
        return True