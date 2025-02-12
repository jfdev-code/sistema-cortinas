from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.utils.exceptions import CortinasException

logger = logging.getLogger(__name__)

async def cortinas_exception_handler(request: Request, exc: CortinasException):
    """
    Manejador global para nuestras excepciones personalizadas
    """
    logger.error(f"Error processing request: {exc.message}", 
                extra={
                    "error_code": exc.error_code,
                    "details": exc.details,
                    "path": str(request.url)
                })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "timestamp": datetime.utcnow().isoformat(),
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url)
        }
    )

# # Ejemplo de uso en cortina_routes.py
# @router.post("/", response_model=CortinaInDB)
# async def crear_nueva_cortina(cortina: CortinaCreate, db: Session = Depends(get_db)):
#     """Crea una nueva cortina verificando dimensiones y stock"""
#     # Validamos dimensiones
#     if cortina.ancho < 20 or cortina.ancho > 500:
#         raise InvalidDimensionsError("ancho", cortina.ancho, 20, 500)
#     if cortina.alto < 20 or cortina.alto > 500:
#         raise InvalidDimensionsError("alto", cortina.alto, 20, 500)
        
#     try:
#         return crear_cortina(db, cortina)
#     except ValueError as e:
#         if "stock insuficiente" in str(e).lower():
#             # Parseamos los items faltantes del mensaje de error
#             raise InsufficientStockError({"items": str(e)})
#         raise CortinasException(
#             message=str(e),
#             error_code="VALIDATION_ERROR",
#             status_code=400
#         )