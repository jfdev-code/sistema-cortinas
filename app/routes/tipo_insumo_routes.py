# app/routes/tipo_insumo_routes.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..schemas.tipo_insumo_schema import TipoInsumoCreate, TipoInsumoUpdate, TipoInsumoInDB
from ..crud.tipo_insumo_crud import (
    create_tipo_insumo,
    get_tipo_insumo,
    get_tipos_insumo,
    update_tipo_insumo,
    delete_tipo_insumo,
    check_tipo_insumo_available
)

router = APIRouter(
    prefix="/tipos-insumo",
    tags=["tipos de insumo"],
    responses={404: {"description": "Tipo de insumo no encontrado"}}
)

@router.post("/", response_model=TipoInsumoInDB)
async def crear_tipo_insumo(
    tipo: TipoInsumoCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new supply type.
    """
    try:
        return await create_tipo_insumo(db=db, tipo=tipo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TipoInsumoInDB])
async def obtener_tipos_insumo(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=2),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of supply types with optional search.
    """
    return await get_tipos_insumo(db, skip=skip, limit=limit, search=search)

@router.get("/{tipo_id}", response_model=TipoInsumoInDB)
async def obtener_tipo_insumo(
    tipo_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific supply type by ID.
    """
    tipo = await get_tipo_insumo(db, tipo_id)
    if tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de insumo no encontrado")
    return tipo

@router.put("/{tipo_id}", response_model=TipoInsumoInDB)
async def actualizar_tipo_insumo(
    tipo_id: int = Path(..., ge=1),
    tipo: TipoInsumoUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing supply type.
    """
    try:
        db_tipo = await update_tipo_insumo(db, tipo_id, tipo)
        if db_tipo is None:
            raise HTTPException(status_code=404, detail="Tipo de insumo no encontrado")
        return db_tipo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{tipo_id}")
async def eliminar_tipo_insumo(
    tipo_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a supply type if it has no references.
    """
    try:
        success = await delete_tipo_insumo(db, tipo_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tipo de insumo no encontrado")
        return {"message": "Tipo de insumo eliminado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{tipo_id}/disponible")
async def verificar_disponibilidad(
    tipo_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a supply type is available for use.
    """
    is_available = await check_tipo_insumo_available(db, tipo_id)
    return {"disponible": is_available}