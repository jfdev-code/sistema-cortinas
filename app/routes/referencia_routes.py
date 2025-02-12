# app/routes/referencia_routes.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..schemas.referencia_insumo_schema import (
    ReferenciaInsumoCreate,
    ReferenciaInsumoUpdate,
    ReferenciaInsumoInDB
)
from ..crud.referencia_crud import (
    create_referencia,
    get_referencia,
    get_referencias,
    get_referencias_by_tipo,
    update_referencia,
    delete_referencia
)

router = APIRouter(
    prefix="/referencias",
    tags=["referencias"],
    responses={404: {"description": "Referencia no encontrada"}}
)

@router.post("/", response_model=ReferenciaInsumoInDB)
async def crear_referencia(
    referencia: ReferenciaInsumoCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new supply reference.
    """
    try:
        return await create_referencia(db=db, referencia=referencia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ReferenciaInsumoInDB])
async def obtener_referencias(
    tipo_insumo_id: Optional[int] = Query(None, ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=2),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of references with optional filtering and search.
    """
    if tipo_insumo_id:
        return await get_referencias_by_tipo(db, tipo_insumo_id)
    return await get_referencias(db, skip=skip, limit=limit, search=search)

@router.get("/{referencia_id}", response_model=ReferenciaInsumoInDB)
async def obtener_referencia(
    referencia_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific reference by ID.
    """
    referencia = await get_referencia(db, referencia_id)
    if referencia is None:
        raise HTTPException(status_code=404, detail="Referencia no encontrada")
    return referencia

@router.put("/{referencia_id}", response_model=ReferenciaInsumoInDB)
async def actualizar_referencia(
    referencia_id: int = Path(..., ge=1),
    referencia: ReferenciaInsumoUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing reference.
    """
    try:
        db_referencia = await update_referencia(db, referencia_id, referencia)
        if db_referencia is None:
            raise HTTPException(status_code=404, detail="Referencia no encontrada")
        return db_referencia
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{referencia_id}")
async def eliminar_referencia(
    referencia_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a reference if it has no dependencies.
    """
    try:
        success = await delete_referencia(db, referencia_id)
        if not success:
            raise HTTPException(status_code=404, detail="Referencia no encontrada")
        return {"message": "Referencia eliminada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tipo/{tipo_id}", response_model=List[ReferenciaInsumoInDB])
async def obtener_referencias_por_tipo(
    tipo_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all references for a specific supply type.
    """
    return await get_referencias_by_tipo(db, tipo_id)