# app/routes/cortina_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..schemas.cortina_schema import CortinaCreate, CortinaUpdate, CortinaInDB
from ..crud.cortina_crud import (
    crear_cortina,
    obtener_cortina,
    get_cortinas,
    update_cortina,
    delete_cortina,
    get_estadisticas_cortinas,
    get_cortinas_by_diseno,
    get_consumo_materiales
)

router = APIRouter(
    prefix="/cortinas",
    tags=["cortinas"],
    responses={404: {"description": "Cortina no encontrada"}}
)

@router.post("/", response_model=CortinaInDB)
async def crear_nueva_cortina(
    cortina: CortinaCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new curtain with the given specifications."""
    try:
        return await crear_cortina(db=db, cortina=cortina)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{cortina_id}", response_model=CortinaInDB)
async def get_cortina_by_id(
    cortina_id: int = Path(..., ge=1, description="ID de la cortina"),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific curtain by ID."""
    db_cortina = await obtener_cortina(db, cortina_id=cortina_id)
    if db_cortina is None:
        raise HTTPException(status_code=404, detail="Cortina no encontrada")
    return db_cortina

@router.get("/", response_model=List[CortinaInDB])
async def obtener_cortinas(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Límite de registros a retornar"),
    estado: Optional[str] = Query(None, description="Estado de la cortina"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicial"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha final"),
    db: AsyncSession = Depends(get_db)
):
    """Get a list of curtains with optional filtering and pagination."""
    return await get_cortinas(
        db,
        skip=skip,
        limit=limit,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

@router.put("/{cortina_id}", response_model=CortinaInDB)
async def actualizar_cortina(
    cortina_id: int = Path(..., ge=1, description="ID de la cortina a actualizar"),
    cortina: CortinaUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing curtain."""
    try:
        db_cortina = await update_cortina(db, cortina_id, cortina)
        if db_cortina is None:
            raise HTTPException(status_code=404, detail="Cortina no encontrada")
        return db_cortina
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{cortina_id}")
async def eliminar_cortina(
    cortina_id: int = Path(..., ge=1, description="ID de la cortina a eliminar"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a curtain and restore its inventory."""
    try:
        success = await delete_cortina(db, cortina_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cortina no encontrada")
        return {"message": "Cortina eliminada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/estadisticas/", response_model=dict)
async def obtener_estadisticas(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get curtain production statistics."""
    return await get_estadisticas_cortinas(
        db,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

@router.get("/diseno/{diseno_id}", response_model=List[CortinaInDB])
async def obtener_cortinas_por_diseno(
    diseno_id: int = Path(..., ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all curtains for a specific design."""
    return await get_cortinas_by_diseno(
        db,
        diseno_id=diseno_id,
        skip=skip,
        limit=limit
    )

@router.get("/consumo/materiales/", response_model=List[dict])
async def obtener_consumo_materiales(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get material consumption statistics."""
    return await get_consumo_materiales(
        db,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )