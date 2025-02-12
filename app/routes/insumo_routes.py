# # app/routes/insumo_routes.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# # Importamos nuestros módulos personalizados
# from ..database import SessionLocal
# from ..schemas.insumo_schema import InsumoCreate, InsumoUpdate, InsumoInDB
# from ..crud.insumo_crud import get_insumo, get_insumos, create_insumo, update_insumo



# # Creamos un router específico para los insumos
# router = APIRouter(
#     prefix="/insumos",
#     tags=["insumos"]
# )

# # Esta función nos ayuda a obtener una conexión a la base de datos
# def get_db():
#     """
#     Crea una nueva sesión de base de datos para cada petición.
#     La sesión se cierra automáticamente cuando termina la petición.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.get("/", response_model=list[InsumoInDB])
# def obtener_insumos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return get_insumos(db, skip=skip, limit=limit)

# @router.post("/", response_model=InsumoInDB)
# def crear_insumo(insumo: InsumoCreate, db: Session = Depends(get_db)):
#     """
#     Crea un nuevo insumo en la base de datos.
#     Los datos del insumo se validan automáticamente usando el esquema InsumoCreate.
#     """
#     return create_insumo(db=db, insumo=insumo)

# @router.get("/{insumo_id}", response_model=InsumoInDB)
# def obtener_insumo(insumo_id: int, db: Session = Depends(get_db)):
#     """
#     Obtiene un insumo específico por su ID.
#     Si el insumo no existe, devuelve un error 404.
#     """
#     db_insumo = get_insumo(db, insumo_id=insumo_id)
#     if db_insumo is None:
#         raise HTTPException(status_code=404, detail="Insumo no encontrado")
#     return db_insumo

# @router.get("/", response_model=List[InsumoInDB])
# def obtener_insumos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     """
#     Obtiene una lista de insumos con paginación.
#     - skip: número de registros a saltar
#     - limit: número máximo de registros a devolver
#     """
#     insumos = get_insumos(db, skip=skip, limit=limit)
#     return insumos

# @router.put("/{insumo_id}", response_model=InsumoInDB)
# def actualizar_insumo(insumo_id: int, insumo: InsumoUpdate, db: Session = Depends(get_db)):
#     """
#     Actualiza un insumo existente.
#     Solo se actualizarán los campos que se envíen en la petición.
#     """
#     db_insumo = update_insumo(db, insumo_id=insumo_id, insumo=insumo)
#     if db_insumo is None:
#         raise HTTPException(status_code=404, detail="Insumo no encontrado")
#     return db_insumo