# app/utils/exceptions.py
from fastapi import HTTPException
from typing import Optional, Any, Dict

class CortinasException(Exception):
    """Base exception for our application"""
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class InsufficientStockError(CortinasException):
    """Raised when there isn't enough stock for an operation"""
    def __init__(self, missing_items: Dict[str, float]):
        super().__init__(
            message="Stock insuficiente para completar la operación",
            error_code="INSUFFICIENT_STOCK",
            status_code=400,
            details={"missing_items": missing_items}
        )

class InvalidDimensionsError(CortinasException):
    """Raised when curtain dimensions are invalid"""
    def __init__(self, dimension: str, value: float, min_value: float, max_value: float):
        super().__init__(
            message=f"Dimensión inválida para {dimension}",
            error_code="INVALID_DIMENSIONS",
            status_code=400,
            details={
                "dimension": dimension,
                "value": value,
                "valid_range": {
                    "min": min_value,
                    "max": max_value
                }
            }
        )

# app/utils/error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

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
