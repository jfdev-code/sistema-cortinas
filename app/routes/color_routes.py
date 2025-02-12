# app/routes/color_routes.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..schemas.color_insumo_schema import ColorInsumoCreate, ColorInsumoUpdate, ColorInsumoInDB
from ..crud.color_crud import (
    create_color,
    get_color,
    get_colores_by_referencia,
    update_color,
    search_colores,
    delete_color,
    get_colores_with_stock
)

router = APIRouter(
    prefix="/colores",
    tags=["colores"],
    responses={404: {"description": "Color no encontrado"}}
)

@router.post("/", response_model=ColorInsumoInDB)
async def crear_color(
    color: ColorInsumoCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new color for a specific supply reference.
    """
    try:
        return await create_color(db=db, color=color)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/referencia/{referencia_id}", response_model=List[ColorInsumoInDB])
async def obtener_colores_por_referencia(
    referencia_id: int = Path(..., ge=1),
    disponibles: bool = Query(False, description="Filtrar solo colores con stock"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all colors available for a specific reference.
    """
    return await get_colores_by_referencia(
        db,
        referencia_id=referencia_id,
        solo_disponibles=disponibles
    )

@router.get("/{color_id}", response_model=ColorInsumoInDB)
async def obtener_color(
    color_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific color by its ID.
    """
    color = await get_color(db, color_id)
    if color is None:
        raise HTTPException(status_code=404, detail="Color no encontrado")
    return color

@router.put("/{color_id}", response_model=ColorInsumoInDB)
async def actualizar_color(
    color_id: int = Path(..., ge=1),
    color: ColorInsumoUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing color.
    """
    try:
        db_color = await update_color(db, color_id, color)
        if db_color is None:
            raise HTTPException(status_code=404, detail="Color no encontrado")
        return db_color
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{color_id}")
async def eliminar_color(
    color_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a color if it has no associated inventory.
    """
    try:
        success = await delete_color(db, color_id)
        if not success:
            raise HTTPException(status_code=404, detail="Color no encontrado")
        return {"message": "Color eliminado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/buscar/", response_model=List[ColorInsumoInDB])
async def buscar_colores(
    termino: str = Query(..., min_length=2),
    referencia_id: Optional[int] = Query(None, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Search colors by name or code.
    """
    return await search_colores(db, termino, referencia_id)

@router.get("/stock/{referencia_id}", response_model=List[ColorInsumoInDB])
async def obtener_colores_con_stock(
    referencia_id: int = Path(..., ge=1),
    cantidad_minima: float = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all colors for a reference that have at least the specified stock.
    """
    return await get_colores_with_stock(
        db,
        referencia_id=referencia_id,
        cantidad_minima=cantidad_minima
    )