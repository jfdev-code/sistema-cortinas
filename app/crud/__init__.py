# app/crud/__init__.py
"""
Async CRUD operations package initialization.
"""

# Import inventory-related operations
from .inventario_crud import (
    verificar_disponibilidad,
    get_inventario_by_color_ref,
    update_stock,
    create_inventario,
    get_inventario,
    get_all_inventario,
    actualizar_inventario,
    delete_inventario,
    get_alertas_stock
)

# Import tipo insumo operations
from .tipo_insumo_crud import (
    create_tipo_insumo,
    get_tipo_insumo,
    get_tipos_insumo,
    update_tipo_insumo,
    delete_tipo_insumo,
    check_tipo_insumo_available
)

# Import reference operations
from .referencia_crud import (
    create_referencia,
    get_referencia,
    get_referencias,
    get_referencias_by_tipo,
    update_referencia,
    delete_referencia
)

# Import color operations
from .color_crud import (
    create_color,
    get_color,
    get_colores_by_referencia,
    update_color,
    search_colores,
    delete_color,
    get_colores_with_stock
)

# Import design operations
from .diseno_crud import (
    create_diseno,
    get_diseno,
    get_diseno_by_codigo,
    get_disenos,
    update_diseno
)

# Import curtain operations
from .cortina_crud import (
    crear_cortina,
    obtener_cortina,
    get_cortinas,
    update_cortina,
    delete_cortina,
    get_estadisticas_cortinas,
    get_cortinas_by_diseno,
    get_consumo_materiales
)

# Export all operations
__all__ = [
    # Inventory operations
    'verificar_disponibilidad',
    'get_inventario_by_color_ref',
    'update_stock',
    'create_inventario',
    'get_inventario',
    'get_all_inventario',
    'actualizar_inventario',
    'delete_inventario',
    'get_alertas_stock',
    
    # Tipo insumo operations
    'create_tipo_insumo',
    'get_tipo_insumo',
    'get_tipos_insumo',
    'update_tipo_insumo',
    'delete_tipo_insumo',
    'check_tipo_insumo_available',
    
    # Reference operations
    'create_referencia',
    'get_referencia',
    'get_referencias',
    'get_referencias_by_tipo',
    'update_referencia',
    'delete_referencia',
    
    # Color operations
    'create_color',
    'get_color',
    'get_colores_by_referencia',
    'update_color',
    'search_colores',
    'delete_color',
    'get_colores_with_stock',
    
    # Design operations
    'create_diseno',
    'get_diseno',
    'get_diseno_by_codigo',
    'get_disenos',
    'update_diseno',
    
    # Curtain operations
    'crear_cortina',
    'obtener_cortina',
    'get_cortinas',
    'update_cortina',
    'delete_cortina',
    'get_estadisticas_cortinas',
    'get_cortinas_by_diseno',
    'get_consumo_materiales'
]