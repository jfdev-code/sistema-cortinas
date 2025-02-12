# app/crud/referencia_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime

from ..models.referencia_insumo import ReferenciaInsumo
from ..schemas.referencia_insumo_schema import (
    ReferenciaInsumoCreate, 
    ReferenciaInsumoUpdate
)
from ..utils.transaction import transaction_scope

async def create_referencia(
    db: AsyncSession,
    referencia: ReferenciaInsumoCreate
) -> ReferenciaInsumo:
    """
    Creates a new supply reference.
    
    Args:
        db: Async database session
        referencia: New reference data
        
    Returns:
        ReferenciaInsumo: The created reference
        
    Raises:
        ValueError: If validation fails or duplicate code exists
    """
    async with transaction_scope(db) as tx:
        # Check for duplicate code
        stmt = select(ReferenciaInsumo).where(
            ReferenciaInsumo.codigo == referencia.codigo
        )
        result = await tx.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Ya existe una referencia con el código {referencia.codigo}")
        
        db_ref = ReferenciaInsumo(**referencia.dict())
        tx.add(db_ref)
        await tx.flush()
        return db_ref

async def get_referencia(
    db: AsyncSession,
    referencia_id: int
) -> Optional[ReferenciaInsumo]:
    """
    Gets a specific reference by its ID.
    
    Args:
        db: Async database session
        referencia_id: ID of the reference to retrieve
        
    Returns:
        Optional[ReferenciaInsumo]: The found reference or None
    """
    stmt = select(ReferenciaInsumo).where(ReferenciaInsumo.id == referencia_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_referencias(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[ReferenciaInsumo]:
    """
    Gets a paginated list of references with optional search.
    
    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term
        
    Returns:
        List[ReferenciaInsumo]: List of references
    """
    query = select(ReferenciaInsumo)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                ReferenciaInsumo.codigo.ilike(search_term),
                ReferenciaInsumo.nombre.ilike(search_term)
            )
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_referencias_by_tipo(
    db: AsyncSession,
    tipo_id: int
) -> List[ReferenciaInsumo]:
    """
    Gets all references associated with a specific supply type.
    
    Args:
        db: Async database session
        tipo_id: ID of the supply type
        
    Returns:
        List[ReferenciaInsumo]: List of associated references
    """
    stmt = (
        select(ReferenciaInsumo)
        .where(ReferenciaInsumo.tipo_insumo_id == tipo_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_referencia(
    db: AsyncSession,
    referencia_id: int,
    referencia: ReferenciaInsumoUpdate
) -> Optional[ReferenciaInsumo]:
    """
    Updates an existing reference.
    
    Args:
        db: Async database session
        referencia_id: ID of the reference to update
        referencia: Updated reference data
        
    Returns:
        Optional[ReferenciaInsumo]: The updated reference or None if not found
    """
    async with transaction_scope(db) as tx:
        # Find the reference
        stmt = select(ReferenciaInsumo).where(ReferenciaInsumo.id == referencia_id)
        result = await tx.execute(stmt)
        db_ref = result.scalar_one_or_none()
        
        if not db_ref:
            return None

        # If code is being updated, check for duplicates
        update_data = referencia.dict(exclude_unset=True)
        if 'codigo' in update_data and update_data['codigo'] != db_ref.codigo:
            dup_stmt = select(ReferenciaInsumo).where(
                ReferenciaInsumo.codigo == update_data['codigo']
            )
            dup_result = await tx.execute(dup_stmt)
            existing = dup_result.scalar_one_or_none()
            if existing:
                raise ValueError(
                    f"Ya existe una referencia con el código {update_data['codigo']}"
                )

        # Update only provided fields
        for field, value in update_data.items():
            setattr(db_ref, field, value)
        
        db_ref.fecha_actualizacion = datetime.utcnow()
        return db_ref

async def delete_referencia(db: AsyncSession, referencia_id: int) -> bool:
    """
    Deletes a reference if it has no dependencies.
    
    Args:
        db: Async database session
        referencia_id: ID of the reference to delete
        
    Returns:
        bool: True if deleted successfully, False if not found
        
    Raises:
        ValueError: If the reference has associated colors or inventory
    """
    async with transaction_scope(db) as tx:
        # Find the reference
        stmt = select(ReferenciaInsumo).where(ReferenciaInsumo.id == referencia_id)
        result = await tx.execute(stmt)
        db_ref = result.scalar_one_or_none()
        
        if not db_ref:
            return False

        # Check for dependencies
        if db_ref.colores or db_ref.inventarios:
            raise ValueError(
                "No se puede eliminar la referencia porque tiene colores o inventario asociado"
            )

        await tx.delete(db_ref)
        return True