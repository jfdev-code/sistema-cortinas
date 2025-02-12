# app/routes/diseno_routes.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..schemas.diseno_schema import DisenoCreate, DisenoUpdate, DisenoInDB
from ..crud.diseno_crud import (
    create_diseno,
    get_diseno,
    get_diseno_by_codigo,
    get_disenos,
    update_diseno
)

router = APIRouter(
    prefix="/disenos",
    tags=["diseños"],
    responses={404: {"description": "Diseño no encontrado"}}
)

@router.post("/", response_model=DisenoInDB)
async def crear_diseno(
    diseno: DisenoCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new curtain design with its associated supplies.
    """
    try:
        return await create_diseno(db=db, diseno=diseno)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[DisenoInDB])
async def obtener_disenos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=2),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of designs with optional search.
    """
    return await get_disenos(db, skip=skip, limit=limit, search=search)

@router.get("/{diseno_id}", response_model=DisenoInDB)
async def obtener_diseno(
    diseno_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific design by its numeric ID.
    """
    diseno = await get_diseno(db, diseno_id)
    if diseno is None:
        raise HTTPException(status_code=404, detail="Diseño no encontrado")
    return diseno

@router.get("/codigo/{id_diseno}", response_model=DisenoInDB)
async def obtener_diseno_por_codigo(
    id_diseno: str = Path(..., min_length=3),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific design by its friendly code.
    """
    diseno = await get_diseno_by_codigo(db, id_diseno)
    if diseno is None:
        raise HTTPException(status_code=404, detail="Diseño no encontrado")
    return diseno

@router.put("/{diseno_id}", response_model=DisenoInDB)
async def actualizar_diseno(
    diseno_id: int = Path(..., ge=1),
    diseno: DisenoUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing design.
    """
    try:
        db_diseno = await update_diseno(db, diseno_id, diseno)
        if db_diseno is None:
            raise HTTPException(status_code=404, detail="Diseño no encontrado")
        return db_diseno
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))