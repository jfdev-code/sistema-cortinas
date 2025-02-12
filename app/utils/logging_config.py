# app/utils/logging_config.py
import logging
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path
import sys
import traceback
from logging.handlers import RotatingFileHandler

from app.models.inventario_insumo import InventarioInsumo

class JSONFormatter(logging.Formatter):
    """
    Formateador personalizado que genera logs en formato JSON
    para mejor integración con herramientas de análisis
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Agregamos excepción si existe
        if record.exc_info:
            log_data["exception"] = {
                "type": str(record.exc_info[0].__name__),
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
            
        # Agregamos datos extra si existen
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
            
        return json.dumps(log_data)

def setup_logging(
    log_path: str = "logs",
    log_level: int = logging.INFO,
    max_size_mb: int = 100,
    backup_count: int = 5
) -> None:
    """
    Configura el sistema de logging con rotación de archivos
    y formato JSON para mejor análisis
    """
    # Creamos el directorio de logs si no existe
    log_dir = Path(log_path)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuramos el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiamos handlers existentes
    root_logger.handlers = []
    
    # Configuramos el handler para archivos
    file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=max_size_mb * 1024 * 1024,  # Convertimos MB a bytes
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Configuramos el handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    root_logger.addHandler(console_handler)
    
    # Configuramos logging específico para SQL Alchemy
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

class LoggerMixin:
    """
    Mixin para agregar capacidades de logging a cualquier clase
    """
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    def log_error(self, message: str, exc_info: bool = True, **extra) -> None:
        """
        Registra un error con información adicional
        """
        self.logger.error(
            message,
            exc_info=exc_info,
            extra={"extra_data": extra}
        )
    
    def log_info(self, message: str, **extra) -> None:
        """
        Registra información con datos adicionales
        """
        self.logger.info(
            message,
            extra={"extra_data": extra}
        )
    
    def log_warning(self, message: str, **extra) -> None:
        """
        Registra una advertencia con datos adicionales
        """
        self.logger.warning(
            message,
            extra={"extra_data": extra}
        )

# # Ejemplo de uso en servicios:
# class InventarioService(LoggerMixin):
#     def __init__(self, db: Session):
#         self.db = db
    
#     async def actualizar_stock(
#         self,
#         inventario_id: int,
#         cantidad: float,
#         motivo: str
#     ) -> None:
#         try:
#             inventario = self.db.query(InventarioInsumo).get(inventario_id)
#             if not inventario:
#                 raise ValueError(f"Inventario {inventario_id} no encontrado")
                
#             cantidad_anterior = inventario.cantidad
#             inventario.cantidad += cantidad
            
#             self.log_info(
#                 "Stock actualizado",
#                 inventario_id=inventario_id,
#                 cantidad_anterior=cantidad_anterior,
#                 nueva_cantidad=inventario.cantidad,
#                 cambio=cantidad,
#                 motivo=motivo
#             )
            
#             # Verificamos si alcanzamos nivel mínimo
#             if inventario.cantidad <= inventario.cantidad_minima:
#                 self.log_warning(
#                     "Stock bajo mínimo",
#                     inventario_id=inventario_id,
#                     cantidad_actual=inventario.cantidad,
#                     cantidad_minima=inventario.cantidad_minima
#                 )
                
#             self.db.commit()
            
#         except Exception as e:
#             self.log_error(
#                 "Error actualizando stock",
#                 inventario_id=inventario_id,
#                 cantidad_solicitada=cantidad,
#                 error=str(e)
#             )
#             raise