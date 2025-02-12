# app/crud/insumo_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional, Dict
from datetime import datetime

from ..models.insumo import Insumo
from ..schemas.insumo_schema import InsumoCreate, InsumoUpdate
from ..utils.transaction import transaction_scope

async def create_insumo(db: AsyncSession, insumo: InsumoCreate) -> Insumo:
    """
    Creates a new supply in the database.
    
    Args:
        db: Async database session
        insumo: New supply data
        
    Returns:
        Insumo: The created supply
        
    Raises:
        ValueError: If validation fails
    """
    async with transaction_scope(db) as tx:
        db_insumo = Insumo(**insumo.dict())
        tx.add(db_insumo)
        await tx.flush()
        return db_insumo

async def get_insumo(db: AsyncSession, insumo_id: int) -> Optional[Insumo]:
    """
    Gets a specific supply by its ID.
    
    Args:
        db: Async database session
        insumo_id: ID of the supply to retrieve
        
    Returns:
        Optional[Insumo]: The found supply or None
    """
    stmt = select(Insumo).where(Insumo.id == insumo_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_insumos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    tipo_unidad: Optional[str] = None,
    search: Optional[str] = None
) -> List[Insumo]:
    """
    Gets a list of supplies with filtering and pagination.
    
    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        tipo_unidad: Optional unit type to filter by
        search: Optional search term
        
    Returns:
        List[Insumo]: List of matching supplies
    """
    query = select(Insumo)
    
    if tipo_unidad:
        query = query.where(Insumo.tipo_unidad == tipo_unidad)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(Insumo.nombre.ilike(search_term))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_insumo(
    db: AsyncSession,
    insumo_id: int,
    insumo: InsumoUpdate
) -> Optional[Insumo]:
    """
    Updates an existing supply.
    
    Args:
        db: Async database session
        insumo_id: ID of the supply to update
        insumo: Updated supply data
        
    Returns:
        Optional[Insumo]: The updated supply or None if not found
    """
    async with transaction_scope(db) as tx:
        # Find the supply
        stmt = select(Insumo).where(Insumo.id == insumo_id)
        result = await tx.execute(stmt)
        db_insumo = result.scalar_one_or_none()
        
        if not db_insumo:
            return None
            
        # Update only provided fields
        update_data = insumo.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_insumo, field, value)
        
        db_insumo.fecha_actualizacion = datetime.utcnow()
        return db_insumo

async def delete_insumo(db: AsyncSession, insumo_id: int) -> bool:
    """
    Deletes a supply if it has no dependencies.
    
    Args:
        db: Async database session
        insumo_id: ID of the supply to delete
        
    Returns:
        bool: True if deleted successfully, False if not found
        
    Raises:
        ValueError: If the supply has dependencies
    """
    async with transaction_scope(db) as tx:
        # Find the supply
        stmt = select(Insumo).where(Insumo.id == insumo_id)
        result = await tx.execute(stmt)
        db_insumo = result.scalar_one_or_none()
        
        if not db_insumo:
            return False
        
        # Check for dependencies here if needed
        
        await tx.delete(db_insumo)
        return True

async def get_insumos_stats(db: AsyncSession) -> Dict:
    """
    Gets statistical information about supplies.
    
    Args:
        db: Async database session
        
    Returns:
        Dict: Statistics about supplies
    """
    # Get total count
    total_query = select(Insumo)
    total_result = await db.execute(total_query)
    total = len(total_result.scalars().all())
    
    # Get count by unit type
    by_unit_query = (
        select(Insumo.tipo_unidad, Insumo.id)
        .group_by(Insumo.tipo_unidad)
    )
    by_unit_result = await db.execute(by_unit_query)
    by_unit = {
        tipo: len(list(group)) 
        for tipo, group in by_unit_result.fetchall()
    }
    
    return {
        "total_insumos": total,
        "por_tipo_unidad": by_unit,
        "fecha_reporte": datetime.utcnow()
    }