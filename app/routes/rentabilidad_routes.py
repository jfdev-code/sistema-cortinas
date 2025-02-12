# app/routes/rentabilidad_routes.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from ..database import get_db
from ..services.rentabilidad_service import calcular_precio_venta

router = APIRouter(
    prefix="/rentabilidad",
    tags=["rentabilidad"]
)

@router.get(
    "/calcular-precio/{cortina_id}",
    summary="Calcular Precio de Venta",
    description="""
    Calcula el precio al que debes vender una cortina para alcanzar la rentabilidad deseada.
    Proporciona un análisis detallado incluyendo costos, márgenes y recomendaciones.
    """
)
async def calcular_precio_rentable(
    cortina_id: int = Path(..., description="ID de la cortina"),
    rentabilidad: float = Query(
        ..., 
        description="Rentabilidad deseada en decimal (ej: 0.30 para 30%)",
        gt=0,
        le=2
    ),
    db: AsyncSession = Depends(get_db)
):
    try:
        resultado = await calcular_precio_venta(db, cortina_id, rentabilidad)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))