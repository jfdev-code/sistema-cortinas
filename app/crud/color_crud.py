# app/crud/color_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime

from ..models.color_insumo import ColorInsumo
from ..models.inventario_insumo import InventarioInsumo
from ..schemas.color_insumo_schema import ColorInsumoCreate, ColorInsumoUpdate
from ..utils.transaction import transaction_scope

async def create_color(db: AsyncSession, color: ColorInsumoCreate) -> ColorInsumo:
    """
    Creates a new color for a specific supply reference.
    
    Args:
        db: Async database session
        color: New color data
        
    Returns:
        ColorInsumo: The created color entry
        
    Raises:
        ValueError: If validation fails or duplicate code exists
    """
    async with transaction_scope(db) as tx:
        # Check if code exists for this reference
        stmt = select(ColorInsumo).where(
            and_(
                ColorInsumo.referencia_id == color.referencia_id,
                ColorInsumo.codigo == color.codigo
            )
        )
        result = await tx.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(
                f"Ya existe un color con el código {color.codigo} para esta referencia"
            )
        
        db_color = ColorInsumo(**color.dict())
        tx.add(db_color)
        await tx.flush()
        return db_color

async def get_color(db: AsyncSession, color_id: int) -> Optional[ColorInsumo]:
    """
    Gets a specific color by its ID.
    
    Args:
        db: Async database session
        color_id: ID of the color to retrieve
        
    Returns:
        Optional[ColorInsumo]: The found color or None
    """
    stmt = select(ColorInsumo).where(ColorInsumo.id == color_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_colores_by_referencia(
    db: AsyncSession,
    referencia_id: int,
    solo_disponibles: bool = False
) -> List[ColorInsumo]:
    """
    Gets all available colors for a specific reference.
    
    Args:
        db: Async database session
        referencia_id: ID of the reference to find colors for
        solo_disponibles: If True, only returns colors with available stock
        
    Returns:
        List[ColorInsumo]: List of matching colors
    """
    query = select(ColorInsumo).where(ColorInsumo.referencia_id == referencia_id)
    
    if solo_disponibles:
        query = (
            query
            .join(ColorInsumo.inventarios)
            .where(InventarioInsumo.cantidad > 0)
            .distinct()
        )
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_color(
    db: AsyncSession,
    color_id: int,
    color_data: ColorInsumoUpdate
) -> Optional[ColorInsumo]:
    """
    Updates an existing color.
    
    Args:
        db: Async database session
        color_id: ID of the color to update
        color_data: Updated color data
        
    Returns:
        Optional[ColorInsumo]: The updated color or None if not found
    """
    async with transaction_scope(db) as tx:
        # Find the color
        stmt = select(ColorInsumo).where(ColorInsumo.id == color_id)
        result = await tx.execute(stmt)
        db_color = result.scalar_one_or_none()
        
        if not db_color:
            return None

        # If code is being updated, check for duplicates
        update_data = color_data.dict(exclude_unset=True)
        if 'codigo' in update_data and update_data['codigo'] != db_color.codigo:
            dup_stmt = select(ColorInsumo).where(
                and_(
                    ColorInsumo.referencia_id == db_color.referencia_id,
                    ColorInsumo.codigo == update_data['codigo']
                )
            )
            dup_result = await tx.execute(dup_stmt)
            existing = dup_result.scalar_one_or_none()
            if existing:
                raise ValueError(
                    f"Ya existe un color con el código {update_data['codigo']} "
                    f"para esta referencia"
                )

        # Update only provided fields
        for field, value in update_data.items():
            setattr(db_color, field, value)
        
        db_color.fecha_actualizacion = datetime.utcnow()
        return db_color

async def search_colores(
    db: AsyncSession,
    termino: str,
    referencia_id: Optional[int] = None
) -> List[ColorInsumo]:
    """
    Searches colors by name or code.
    
    Args:
        db: Async database session
        termino: Search term to filter by
        referencia_id: Optional reference ID to filter by
        
    Returns:
        List[ColorInsumo]: List of matching colors
    """
    # Create base query
    query = select(ColorInsumo)
    
    # Add search condition
    search_term = f"%{termino}%"
    query = query.where(
        or_(
            ColorInsumo.nombre.ilike(search_term),
            ColorInsumo.codigo.ilike(search_term)
        )
    )
    
    # Add reference filter if provided
    if referencia_id:
        query = query.where(ColorInsumo.referencia_id == referencia_id)
    
    # Order by relevance and name
    query = query.order_by(ColorInsumo.nombre)
    
    result = await db.execute(query)
    return result.scalars().all()

async def delete_color(db: AsyncSession, color_id: int) -> bool:
    """
    Deletes a color if it has no associated inventory.
    
    Args:
        db: Async database session
        color_id: ID of the color to delete
        
    Returns:
        bool: True if deleted successfully, False if not found
        
    Raises:
        ValueError: If the color has associated inventory
    """
    async with transaction_scope(db) as tx:
        # Find the color
        stmt = select(ColorInsumo).where(ColorInsumo.id == color_id)
        result = await tx.execute(stmt)
        db_color = result.scalar_one_or_none()
        
        if not db_color:
            return False

        # Check for inventory
        inv_stmt = select(InventarioInsumo).where(
            InventarioInsumo.color_id == color_id
        )
        inv_result = await tx.execute(inv_stmt)
        if inv_result.first():
            raise ValueError(
                "No se puede eliminar el color porque tiene inventario asociado"
            )

        await tx.delete(db_color)
        return True

async def get_colores_with_stock(
    db: AsyncSession,
    referencia_id: int,
    cantidad_minima: float = 0
) -> List[ColorInsumo]:
    """
    Gets all colors for a reference that have at least the specified stock.
    
    Args:
        db: Async database session
        referencia_id: ID of the reference to check
        cantidad_minima: Minimum stock quantity required
        
    Returns:
        List[ColorInsumo]: List of colors with sufficient stock
    """
    query = (
        select(ColorInsumo)
        .join(ColorInsumo.inventarios)
        .where(
            and_(
                ColorInsumo.referencia_id == referencia_id,
                InventarioInsumo.cantidad >= cantidad_minima
            )
        )
        .order_by(ColorInsumo.nombre)
    )
    
    result = await db.execute(query)
    return result.scalars().all()