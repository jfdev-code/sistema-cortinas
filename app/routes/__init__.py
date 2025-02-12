# app/routes/__init__.py
"""
This module initializes and exports all routers for the application.
Each router handles a specific set of related endpoints.
"""

from .tipo_insumo_routes import router as tipo_insumo_routes
from .referencia_routes import router as referencia_routes
from .color_routes import router as color_routes
from .inventario_routes import router as inventario_routes
from .diseno_routes import router as diseno_routes
from .cortina_routes import router as cortina_routes
from .rentabilidad_routes import router as rentabilidad_routes

# Export all routers to be available when importing from app.routes
__all__ = [
    'tipo_insumo_routes',
    'referencia_routes',
    'color_routes',
    'inventario_routes',
    'diseno_routes',
    'cortina_routes',
    'rentabilidad_routes'
]