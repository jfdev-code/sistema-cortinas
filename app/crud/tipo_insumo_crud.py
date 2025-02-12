# app/crud/tipo_insumo_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from ..models.tipo_insumo import TipoInsumo
from ..schemas.tipo_insumo_schema import TipoInsumoCreate, TipoInsumoUpdate
from ..utils.transaction import transaction_scope

async def create_tipo_insumo(db: AsyncSession, tipo: TipoInsumoCreate) -> TipoInsumo:
    """
    Creates a new supply type in the database.
    
    Args:
        db: Async database session
        tipo: New supply type data
        
    Returns:
        TipoInsumo: The created supply type
        
    Raises:
        ValueError: If validation fails
    """
    async with transaction_scope(db) as tx:
        # Check if name already exists
        stmt = select(TipoInsumo).where(TipoInsumo.nombre == tipo.nombre)
        result = await tx.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Ya existe un tipo de insumo con el nombre {tipo.nombre}")
        
        db_tipo = TipoInsumo(**tipo.dict())
        tx.add(db_tipo)
        await tx.flush()
        return db_tipo

async def get_tipo_insumo(db: AsyncSession, tipo_id: int) -> Optional[TipoInsumo]:
    """
    Gets a specific supply type by its ID.
    
    Args:
        db: Async database session
        tipo_id: ID of the supply type to retrieve
        
    Returns:
        Optional[TipoInsumo]: The found supply type or None
    """
    stmt = select(TipoInsumo).where(TipoInsumo.id == tipo_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_tipos_insumo(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[TipoInsumo]:
    """
    Gets a paginated list of supply types with optional search.
    
    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
# app/crud/tipo_insumo_crud.py (continuation)
    : Maximum number of records to return
    search: Optional search term
    
    Returns:
        List[TipoInsumo]: List of supply types
    """
    query = select(TipoInsumo)
    
    if search:
        query = query.where(TipoInsumo.nombre.ilike(f"%{search}%"))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_tipo_insumo(
    db: AsyncSession,
    tipo_id: int,
    tipo: TipoInsumoUpdate
) -> Optional[TipoInsumo]:
    """
    Updates an existing supply type.
    
    Args:
        db: Async database session
        tipo_id: ID of the supply type to update
        tipo: Updated supply type data
        
    Returns:
        Optional[TipoInsumo]: The updated supply type or None if not found
    """
    async with transaction_scope(db) as tx:
        # Find the supply type
        stmt = select(TipoInsumo).where(TipoInsumo.id == tipo_id)
        result = await tx.execute(stmt)
        db_tipo = result.scalar_one_or_none()
        
        if not db_tipo:
            return None

        # If name is being updated, check for duplicates
        update_data = tipo.dict(exclude_unset=True)
        if 'nombre' in update_data and update_data['nombre'] != db_tipo.nombre:
            dup_stmt = select(TipoInsumo).where(TipoInsumo.nombre == update_data['nombre'])
            dup_result = await tx.execute(dup_stmt)
            existing = dup_result.scalar_one_or_none()
            if existing:
                raise ValueError(f"Ya existe un tipo de insumo con el nombre {update_data['nombre']}")

        # Update only provided fields
        for field, value in update_data.items():
            setattr(db_tipo, field, value)
        
        db_tipo.fecha_actualizacion = datetime.utcnow()
        return db_tipo

async def delete_tipo_insumo(db: AsyncSession, tipo_id: int) -> bool:
    """
    Deletes a supply type if it has no associated references.
    
    Args:
        db: Async database session
        tipo_id: ID of the supply type to delete
        
    Returns:
        bool: True if deleted successfully, False if not found
        
    Raises:
        ValueError: If the supply type has associated references
    """
    async with transaction_scope(db) as tx:
        # Find the supply type
        stmt = select(TipoInsumo).where(TipoInsumo.id == tipo_id)
        result = await tx.execute(stmt)
        db_tipo = result.scalar_one_or_none()
        
        if not db_tipo:
            return False

        # Check for references
        references_stmt = select(TipoInsumo).where(
            TipoInsumo.id == tipo_id
        ).join(TipoInsumo.referencias)
        refs_result = await tx.execute(references_stmt)
        if refs_result.scalar_one_or_none():
            raise ValueError(
                "No se puede eliminar el tipo de insumo porque tiene referencias asociadas"
            )

        await tx.delete(db_tipo)
        return True

async def check_tipo_insumo_available(
    db: AsyncSession, 
    tipo_id: int
) -> bool:
    """
    Checks if a supply type is available for use.
    
    Args:
        db: Async database session
        tipo_id: ID of the supply type to check
        
    Returns:
        bool: True if available, False otherwise
    """
    stmt = select(TipoInsumo).where(
        and_(
            TipoInsumo.id == tipo_id,
            TipoInsumo.activo == True
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None



