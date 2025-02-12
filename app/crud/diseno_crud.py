# app/crud/diseno_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime

from ..models.diseno import Diseno, DisenoTipoInsumo
from ..schemas.diseno_schema import DisenoCreate, DisenoUpdate
from ..utils.transaction import transaction_scope

async def create_diseno(
    db: AsyncSession,
    design_data: dict,
    tipos_insumo: dict
) -> Diseno:
    """
    Creates a design with its required material types.
    Now only associates types of materials, not specific references.
    """
    # Create the design first
    diseno = Diseno(
        id_diseno=design_data["codigo"],
        nombre=design_data["nombre"],
        descripcion=design_data["descripcion"],
        costo_mano_obra=design_data["costo_mano_obra"],
        complejidad=design_data["complejidad"]
    )
    db.add(diseno)
    await db.flush()  # Get the ID
    
    # Add the required material types
    for material in design_data["tipos_insumo"]:
        tipo_insumo_rel = DisenoTipoInsumo(
            diseno_id=diseno.id,
            tipo_insumo_id=tipos_insumo[material["tipo_insumo"]].id,
            cantidad_por_metro=material["cantidad_por_metro"],
            descripcion=material["descripcion"]
        )
        db.add(tipo_insumo_rel)
    
    return diseno

async def get_diseno(db: AsyncSession, diseno_id: int) -> Optional[Diseno]:
    """
    Get a design by its numeric ID with eager loading of related types and cortinas.
    
    Args:
        db: Async database session
        diseno_id: ID of the design to retrieve
        
    Returns:
        Optional[Diseno]: The found design or None
    """
    stmt = (
        select(Diseno)
        .options(joinedload(Diseno.tipos_insumo))
        .options(joinedload(Diseno.cortinas))
        .where(Diseno.id == diseno_id)
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()

async def get_diseno_by_codigo(db: AsyncSession, id_diseno: str) -> Optional[Diseno]:
    """
    Get a design by its friendly code with eager loading of related types and cortinas.
    
    Args:
        db: Async database session
        id_diseno: Friendly code of the design
        
    Returns:
        Optional[Diseno]: The found design or None
    """
    stmt = (
        select(Diseno)
        .options(joinedload(Diseno.tipos_insumo))
        .options(joinedload(Diseno.cortinas))
        .where(Diseno.id_diseno == id_diseno)
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()

async def get_disenos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[Diseno]:
    """
    Get a paginated list of designs with optional search and eager loading.
    
    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term
        
    Returns:
        List[Diseno]: List of matching designs
    """
    # Create base query with eager loading
    query = (
        select(Diseno)
        .options(joinedload(Diseno.tipos_insumo))
        .options(joinedload(Diseno.cortinas))
    )
    
    # Add search filter if search term is provided
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Diseno.nombre.ilike(search_term),
                Diseno.id_diseno.ilike(search_term)
            )
        )
    
    # Add pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    return result.unique().scalars().all()

async def update_diseno(
    db: AsyncSession,
    diseno_id: int,
    diseno_data: DisenoUpdate
) -> Optional[Diseno]:
    """
    Update an existing design.
    
    Args:
        db: Async database session
        diseno_id: ID of the design to update
        diseno_data: Updated design data
        
    Returns:
        Optional[Diseno]: The updated design or None if not found
    """
    async with transaction_scope(db) as tx:
        # Find the existing design with its current types and cortinas
        stmt = (
            select(Diseno)
            .options(joinedload(Diseno.tipos_insumo))
            .options(joinedload(Diseno.cortinas))
            .where(Diseno.id == diseno_id)
        )
        result = await tx.execute(stmt)
        db_diseno = result.unique().scalar_one_or_none()
        
        if not db_diseno:
            return None

        # Update basic fields
        update_data = diseno_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field != "tipos_insumo":
                setattr(db_diseno, field, value)

        # Update supply types if provided
        if diseno_data.tipos_insumo:
            # Remove existing relationships
            del_stmt = DisenoTipoInsumo.__table__.delete().where(
                DisenoTipoInsumo.diseno_id == diseno_id
            )
            await tx.execute(del_stmt)
            
            # Create new relationships
            new_tipos_insumo = []
            for tipo_insumo in diseno_data.tipos_insumo:
                db_diseno_insumo = DisenoTipoInsumo(
                    diseno_id=diseno_id,
                    tipo_insumo_id=tipo_insumo.tipo_insumo_id,
                    referencia_id=tipo_insumo.referencia_id,  # Use referencia_id instead of color_id
                    cantidad_por_metro=tipo_insumo.cantidad_por_metro,
                    descripcion=tipo_insumo.descripcion
                )
                tx.add(db_diseno_insumo)
                new_tipos_insumo.append(db_diseno_insumo)
            
            # Update the tipos_insumo relationship
            db_diseno.tipos_insumo = new_tipos_insumo

        db_diseno.fecha_actualizacion = datetime.utcnow()
        return db_diseno