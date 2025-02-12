# app/models/__init__.py
"""Initializes all models in the correct dependency order."""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Naming convention for database constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

# Create a base specifically for models
Base = declarative_base(metadata=metadata)

# Import models in dependency order
from .tipo_insumo import TipoInsumo
from .referencia_insumo import ReferenciaInsumo
from .color_insumo import ColorInsumo
from .diseno import Diseno, DisenoTipoInsumo
from .inventario_insumo import InventarioInsumo
from .cortina import Cortina
from .reserva_inventario import ReservaInventario

__all__ = [
    'Base',
    'TipoInsumo',
    'ReferenciaInsumo',
    'ColorInsumo',
    'InventarioInsumo',
    'Diseno',
    'DisenoTipoInsumo',
    'Cortina',
    'ReservaInventario'
]