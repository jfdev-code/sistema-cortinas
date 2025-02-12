# app/routes/inventario_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional

from ..database import get_db
from ..schemas.inventario_schema import (
    InventarioInsumoCreate,
    InventarioInsumoUpdate,
    InventarioInsumoInDB,
    MovimientoInventario
)
from ..crud.inventario_crud import (
    create_inventario,
    get_inventario,
    get_all_inventario,
    update_stock,
    delete_inventario,
    get_alertas_stock,
    verificar_disponibilidad
)

router = APIRouter(
    prefix="/inventario",
    tags=["inventario"],
    responses={404: {"description": "Inventario no encontrado"}}
)

@router.post("/", response_model=InventarioInsumoInDB)
async def crear_inventario(
    inventario: InventarioInsumoCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new inventory record.
    """
    try:
        return await create_inventario(db=db, inventario=inventario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[InventarioInsumoInDB])
async def obtener_inventario(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    solo_bajo_minimo: bool = Query(False, description="Solo mostrar items bajo mínimo"),
    tipo_insumo_id: Optional[int] = Query(None, description="Filtrar por tipo de insumo"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of inventory records with filtering options.
    """
    return await get_all_inventario(
        db,
        skip=skip,
        limit=limit,
        solo_bajo_minimo=solo_bajo_minimo,
        tipo_insumo_id=tipo_insumo_id
    )

@router.put("/{inventario_id}/stock", response_model=Dict)
async def actualizar_stock(
    inventario_id: int = Path(..., ge=1),
    movimiento: MovimientoInventario = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update stock levels for an inventory item.
    """
    try:
        inventario, nivel_bajo = await update_stock(db, inventario_id, movimiento)
        return {
            "mensaje": "Stock actualizado correctamente",
            "nuevo_stock": inventario.cantidad,
            "alerta_nivel_bajo": nivel_bajo
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/alertas", response_model=List[Dict])
async def obtener_alertas(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of inventory alerts.
    """
    return await get_alertas_stock(db)

# @router.get("/stats", response_model=Dict)
# async def obtener_estadisticas(
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Get inventory statistics.
#     """
#     return await get_inventario_stats(db)

# @router.get("/movimientos", response_model=List[Dict])
# async def obtener_movimientos(
#     dias: int = Query(30, ge=1, le=365, description="Días hacia atrás a consultar"),
#     limit: int = Query(100, ge=1, le=1000, description="Límite de movimientos"),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Get recent inventory movements.
#     """
#     return await get_movimientos_recientes(db, dias=dias, limit=limit)

@router.get("/verificar-disponibilidad/{referencia_id}/{color_id}")
async def verificar_stock_disponible(
    referencia_id: int = Path(..., ge=1),
    color_id: int = Path(..., ge=1),
    cantidad: float = Query(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if there's enough stock available.
    """
    disponible = await verificar_disponibilidad(
        db,
        referencia_id=referencia_id,
        color_id=color_id,
        cantidad_requerida=cantidad
    )
    return {"disponible": disponible}

@router.delete("/{inventario_id}")
async def eliminar_inventario(
    inventario_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an inventory record.
    """
    try:
        success = await delete_inventario(db, inventario_id)
        if not success:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")
        return {"message": "Registro de inventario eliminado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))