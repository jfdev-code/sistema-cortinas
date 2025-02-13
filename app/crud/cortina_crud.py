# app/crud/cortina_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from datetime import datetime

from app.crud.referencia_crud import get_referencia

# Import our models
from ..models.cortina import Cortina
from ..models.diseno import Diseno, DisenoTipoInsumo
from ..models.inventario_insumo import InventarioInsumo
from ..models.referencia_insumo import ReferenciaInsumo
from ..models.tipo_insumo import TipoInsumo
from ..models.color_insumo import ColorInsumo

# Import schemas and utilities
from ..schemas.cortina_schema import CortinaCreate, CortinaUpdate
from ..schemas.inventario_schema import MovimientoInventario
from ..utils.exceptions import CortinasException
from ..utils.transaction import transaction_scope
from ..crud.inventario_crud import get_inventario_by_color_ref, update_stock

async def get_diseno_con_relaciones(db: AsyncSession, diseno_id: int) -> Optional[Diseno]:
    """
    Carga un diseño con todas sus relaciones y precios.
    """
    print("\n=== Debugging get_diseno_con_relaciones ===")
    stmt = (
        select(Diseno)
        .options(
            selectinload(Diseno.tipos_insumo).joinedload(DisenoTipoInsumo.tipo_insumo),
            selectinload(Diseno.tipos_insumo).joinedload(DisenoTipoInsumo.referencia),
            selectinload(Diseno.tipos_insumo).joinedload(DisenoTipoInsumo.color)
        )
        .where(Diseno.id == diseno_id)
    )
    
    result = await db.execute(stmt)
    diseno = result.unique().scalar_one_or_none()
    
    if diseno:
        print(f"Diseño cargado: {diseno.nombre}")
        for tipo_insumo in diseno.tipos_insumo:
            print(f"Tipo insumo: {tipo_insumo.tipo_insumo.nombre}")
            if tipo_insumo.referencia:
                print(f"Referencia: {tipo_insumo.referencia.codigo}, Precio: {tipo_insumo.referencia.precio_unitario}")
            else:
                print("No se encontró referencia")
    
    return diseno

async def verificar_relaciones_diseno(db: AsyncSession, diseno_id: int):
    """
    Verifica las relaciones y referencias del diseño.
    """
    print("\n=== Verificando Relaciones del Diseño ===")
    
    # Consulta para verificar DisenoTipoInsumo
    stmt = text("""
        SELECT 
            d.nombre as diseno_nombre,
            dti.tipo_insumo_id,
            dti.referencia_id,
            ti.nombre as tipo_nombre,
            r.codigo as referencia_codigo,
            r.precio_unitario
        FROM disenos d
        JOIN diseno_tipos_insumo dti ON d.id = dti.diseno_id
        JOIN tipos_insumo ti ON dti.tipo_insumo_id = ti.id
        LEFT JOIN referencias_insumo r ON dti.referencia_id = r.id
        WHERE d.id = :diseno_id
    """)
    
    result = await db.execute(stmt, {"diseno_id": diseno_id})
    relaciones = await result.fetchall()
    
    for rel in relaciones:
        print(f"Diseño: {rel.diseno_nombre}")
        print(f"Tipo Insumo: {rel.tipo_nombre} (ID: {rel.tipo_insumo_id})")
        print(f"Referencia ID: {rel.referencia_id}")
        print(f"Referencia Código: {rel.referencia_codigo}")
        print(f"Precio Unitario: {rel.precio_unitario}")

async def crear_cortina(db: AsyncSession, cortina: CortinaCreate) -> Cortina:
    async with transaction_scope(db) as tx:
        print("\n=== Creando Nueva Cortina ===")
        print(f"Datos recibidos: {cortina.dict()}")

        precio = 0
        
        # Verificar que los tipos_insumo contengan las referencias correctas
        if cortina.tipos_insumo:
            for tipo in cortina.tipos_insumo:
                print(f"Tipo insumo recibido: {tipo}")
                if 'referencia_id' in tipo:
                    # Verificar que la referencia existe y tiene precio
                    ref_stmt = select(ReferenciaInsumo).where(
                        ReferenciaInsumo.id == tipo['referencia_id']
                    )
                    ref_result = await db.execute(ref_stmt)
                    referencia = ref_result.scalar_one_or_none()
                    if referencia:
                        print(f"Referencia encontrada: {referencia.codigo}, Precio: {referencia.precio_unitario}")
                        precio += referencia.precio_unitario
                    else:
                        print(f"⚠️ No se encontró la referencia con ID {tipo['referencia_id']}")

    """
    Crea una nueva cortina con sus cálculos y actualizaciones de inventario.
    """
    async with transaction_scope(db) as tx:
        # Verificar el diseño
        diseno = await get_diseno_con_relaciones(db, cortina.diseno_id)
        if not diseno:
            raise ValueError(f"Diseño con ID {cortina.diseno_id} no encontrado")

        # Verificar stock
        errores_stock = await verificar_stock_suficiente(tx, cortina, diseno)
        if errores_stock:
            raise ValueError(f"Stock insuficiente: {', '.join(errores_stock)}")

        # Crear la cortina
        db_cortina = Cortina(
            diseno_id=cortina.diseno_id,
            ancho=cortina.ancho,
            alto=cortina.alto,
            partida=cortina.partida,
            multiplicador=cortina.multiplicador,
            estado="pendiente",
            notas=cortina.notas or "",
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow()
        )
        
        tx.add(db_cortina)
        await tx.flush()

        rentabilidad_fija = 1.30

        # Calcular costos
        costos = await calcular_costos_detallados(tx, db_cortina, diseno,precio)
        db_cortina.costo_materiales = costos['materiales']
        db_cortina.costo_mano_obra = costos['mano_obra']
        db_cortina.costo_total = costos['total']

        # Actualizar inventario
        await actualizar_inventario_cortina(tx, db_cortina, diseno)
        
        return db_cortina

async def obtener_cortina(db: AsyncSession, cortina_id: int) -> Optional[Cortina]:
    """
    Retrieves a specific curtain by its ID with comprehensive eager loading.
    
    Args:
        db: Async database session
        cortina_id: ID of the curtain to retrieve
        
    Returns:
        Optional[Cortina]: The found curtain or None
    """
    stmt = (
        select(Cortina)
        .options(
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.tipo_insumo),
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.referencia),
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.color)
        )
        .where(Cortina.id == cortina_id)
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()

async def get_cortinas(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
) -> List[Cortina]:
    """
    Retrieves a list of curtains with optional filtering and comprehensive eager loading.
    
    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        estado: Optional status filter
        fecha_inicio: Optional start date filter
        fecha_fin: Optional end date filter
        
    Returns:
        List[Cortina]: List of matching curtains
    """
    query = (
        select(Cortina)
        .options(
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.tipo_insumo),
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.referencia),
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.color)
        )
    )
    
    if estado:
        query = query.where(Cortina.estado == estado)
    
    if fecha_inicio:
        query = query.where(Cortina.fecha_creacion >= fecha_inicio)
    
    if fecha_fin:
        query = query.where(Cortina.fecha_creacion <= fecha_fin)
    
    query = query.order_by(Cortina.fecha_creacion.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.unique().scalars().all()

async def update_cortina(
    db: AsyncSession,
    cortina_id: int,
    cortina_data: CortinaUpdate
) -> Optional[Cortina]:
    """
    Updates an existing curtain with comprehensive inventory management.
    
    Args:
        db: Async database session
        cortina_id: ID of the curtain to update
        cortina_data: Updated curtain data
        
    Returns:
        Optional[Cortina]: The updated curtain or None if not found
        
    Raises:
        ValueError: If inventory adjustments fail
    """
    async with transaction_scope(db) as tx:
        # Find the curtain with relationships
        db_cortina = await obtener_cortina(tx, cortina_id)
        if not db_cortina:
            return None

        # Store original values for inventory adjustment
        old_ancho = db_cortina.ancho
        old_alto = db_cortina.alto
        old_multiplicador = db_cortina.multiplicador

        # Update provided fields
        update_data = cortina_data.dict(exclude_unset=True)
        
        # Update all fields including potentially the estado
        for field, value in update_data.items():
            setattr(db_cortina, field, value)

        # Get design with loaded relationships
        diseno = db_cortina.diseno

        # If dimensions changed, recalculate costs and adjust inventory
        if (db_cortina.ancho != old_ancho or 
            db_cortina.alto != old_alto or 
            db_cortina.multiplicador != old_multiplicador):
            
            # Reverse previous inventory changes
            await revertir_cambios_inventario(
                tx, db_cortina, diseno,
                old_ancho, old_alto, old_multiplicador
            )
            
            # Calculate new costs
            db_cortina.costo_total = await calcular_costos_detallados(tx, db_cortina, diseno)
            
            # Update inventory with new quantities
            await actualizar_inventario_cortina(tx, db_cortina, diseno)

        db_cortina.fecha_actualizacion = datetime.utcnow()
        return db_cortina

async def delete_cortina(db: AsyncSession, cortina_id: int) -> bool:
    """
    Deletes a curtain and restores inventory.
    
    Can only delete curtains in 'pendiente' status to prevent
    data inconsistencies with completed orders.
    
    Args:
        db: Async database session
        cortina_id: ID of the curtain to delete
        
    Returns:
        bool: True if deleted successfully, False if not found
        
    Raises:
        ValueError: If the curtain cannot be deleted
    """
    async with transaction_scope(db) as tx:
        db_cortina = await obtener_cortina(tx, cortina_id)
        if not db_cortina:
            return False
            
        if db_cortina.estado != "pendiente":
            raise ValueError("Only pending curtains can be deleted")
            
        # Get design with loaded relationships
        diseno = db_cortina.diseno

        # Restore inventory
        await revertir_cambios_inventario(
            tx, db_cortina, diseno,
            db_cortina.ancho, db_cortina.alto,
            db_cortina.multiplicador
        )
        
        await tx.delete(db_cortina)
        return True

async def calcular_costos_detallados(db: AsyncSession, cortina: Cortina, diseno: Diseno, precio) -> dict:
    """
    Calcula los costos incluyendo logging detallado.
    """
    print("\n=== Debugging calcular_costos_detallados ===")
    costos = {
        "materiales": 0.0,
        "mano_obra": float(diseno.costo_mano_obra or 0),
        "total": 0.0
    }
    
    print(f"Costo mano de obra base: {costos['mano_obra']}")
    
    # for tipo_insumo_rel in diseno.tipos_insumo:
    #     print(f"\nProcesando tipo insumo: {tipo_insumo_rel.tipo_insumo.nombre}")
        
    #     # Intentamos obtener la referencia actualizada
    #     referencia_stmt = select(ReferenciaInsumo).where(
    #         ReferenciaInsumo.id == tipo_insumo_rel.referencia_id
    #     )
    #     referencia_result = await db.execute(referencia_stmt)
    #     referencia = referencia_result.scalar_one_or_none()
        
    #     if referencia:
    #         print(f"Referencia encontrada: {referencia.codigo}")
    #         print(f"Precio unitario: {referencia.precio_unitario}")
            
    #         metros_necesarios = (
    #             tipo_insumo_rel.cantidad_por_metro * 
    #             (cortina.ancho / 100) *
    #             cortina.multiplicador
    #         )
            
    #         costo_material = metros_necesarios * precio
    #         costos["materiales"] += costo_material
            
    #         print(f"Metros necesarios: {metros_necesarios}")
    #         print(f"Costo material: {costo_material}")
    #     else:
    #         print("⚠️ No se encontró la referencia")
    
    # Aplicar factores
    costos["materiales"] = precio * (cortina.ancho / 100) * cortina.multiplicador

    # factor_complejidad = {
    #     'bajo': 0.8,
    #     'medio': 1.0,
    #     'alto': 1.3
    # }.get(diseno.complejidad, 1.0)
    
    # print(f"\nFactor complejidad: {factor_complejidad}")
    # costos["mano_obra"] *= factor_complejidad
    
    # if cortina.ancho > 300 or cortina.alto > 250:
    #     print("Aplicando factor por tamaño grande (1.15)")
    #     costos["materiales"] *= 1.15
    #     costos["mano_obra"] *= 1.15

    rentabilidad_fija = 1.30
    
    costos["total"] = round((costos["materiales"] + costos["mano_obra"]) * rentabilidad_fija , 2)
    print(f"\nCostos finales:")
    print(f"Materiales: {costos['materiales']}")
    print(f"Mano de obra: {costos['mano_obra']}")
    print(f"Total: {costos['total']}")
    
    return costos



async def verificar_stock_suficiente(
    db: AsyncSession,
    cortina: CortinaCreate,
    diseno: Diseno
) -> List[str]:
    """
    Verify if there's enough stock to manufacture the curtain.
    
    Args:
        db: Async database session
        cortina: The curtain creation data
        diseno: The design with loaded relationships
        
    Returns:
        List[str]: List of error messages for insufficient stock
    """
    errores = []
    
    for tipo_insumo_rel in diseno.tipos_insumo:
        if (not tipo_insumo_rel.referencia or 
            not tipo_insumo_rel.color or 
            not tipo_insumo_rel.tipo_insumo):
            continue

        cantidad_necesaria = (
            tipo_insumo_rel.cantidad_por_metro * 
            (cortina.ancho / 100) * 
            cortina.multiplicador
        )
        
        inventario = await get_inventario_by_color_ref(
            db,
            referencia_id=tipo_insumo_rel.referencia_id,
            color_id=tipo_insumo_rel.color_id
        )
        
        if not inventario or inventario.cantidad < cantidad_necesaria:
            errores.append(
                f"Insufficient stock of {tipo_insumo_rel.tipo_insumo.nombre}: "
                f"needed {cantidad_necesaria:.2f} units"
            )
    
    return errores

async def actualizar_inventario_cortina(
    db: AsyncSession,
    cortina: Cortina,
    diseno: Diseno
) -> None:
    """
    Update inventory when creating a curtain, discounting necessary materials.
    
    Args:
        db: Async database session
        cortina: The curtain object
        diseno: The design with loaded relationships
        
    Raises:
        ValueError: If inventory record is not found
    """
    for tipo_insumo_rel in diseno.tipos_insumo:
        if (not tipo_insumo_rel.referencia or 
            not tipo_insumo_rel.color):
            continue

        cantidad_necesaria = (
            tipo_insumo_rel.cantidad_por_metro * 
            (cortina.ancho / 100) * 
            cortina.multiplicador
        )
        
        inventario = await get_inventario_by_color_ref(
            db,
            referencia_id=tipo_insumo_rel.referencia_id,
            color_id=tipo_insumo_rel.color_id
        )
        
        if inventario:
            movimiento = MovimientoInventario(
                cantidad=cantidad_necesaria,
                tipo_movimiento="salida",
                motivo=f"Manufacturing of curtain ID: {cortina.id}"
            )
            await update_stock(db, inventario.id, movimiento)
        else:
            raise ValueError(
                f"No inventory record found for reference {tipo_insumo_rel.referencia.codigo} "
                f"with color {tipo_insumo_rel.color.codigo}"
            )

async def revertir_cambios_inventario(
    db: AsyncSession,
    cortina: Cortina,
    diseno: Diseno,
    ancho: float,
    alto: float,
    multiplicador: int
) -> None:
    """
    Revert inventory changes for a curtain, restoring previously used materials.
    
    This function is used when:
    1. A curtain is being deleted
    2. A curtain's dimensions are being modified
    3. A mistake needs to be corrected
    
    Args:
        db: Async database session
        cortina: The curtain object
        diseno: The design with loaded relationships
        ancho: Original width that was used
        alto: Original height that was used
        multiplicador: Original multiplier that was used
        
    Raises:
        ValueError: If inventory record is not found
    """
    for tipo_insumo_rel in diseno.tipos_insumo:
        if (not tipo_insumo_rel.referencia or 
            not tipo_insumo_rel.color):
            continue

        # Calculate the quantity that was originally used
        cantidad_necesaria = (
            tipo_insumo_rel.cantidad_por_metro * 
            (ancho / 100) * 
            multiplicador
        )
        
        inventario = await get_inventario_by_color_ref(
            db,
            referencia_id=tipo_insumo_rel.referencia_id,
            color_id=tipo_insumo_rel.color_id
        )
        
        if inventario:
            movimiento = MovimientoInventario(
                cantidad=cantidad_necesaria,
                tipo_movimiento="entrada",
                motivo=f"Reversal for curtain ID: {cortina.id}"
            )
            await update_stock(db, inventario.id, movimiento)
        else:
            raise ValueError(
                f"No inventory record found for reference {tipo_insumo_rel.referencia.codigo} "
                f"with color {tipo_insumo_rel.color.codigo}"
            )

async def get_estadisticas_cortinas(
    db: AsyncSession,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
) -> Dict[str, any]:
    """
    Generate comprehensive statistics about curtain production.
    
    This function calculates:
    1. Total number of curtains produced
    2. Average production time
    3. Most popular designs
    4. Revenue statistics
    5. Material usage patterns
    
    Args:
        db: Async database session
        fecha_inicio: Optional start date for the statistics
        fecha_fin: Optional end date for the statistics
        
    Returns:
        Dict containing various statistics about curtain production
    """
    query = select(Cortina).options(
        selectinload(Cortina.diseno)
    )
    
    if fecha_inicio:
        query = query.where(Cortina.fecha_creacion >= fecha_inicio)
    if fecha_fin:
        query = query.where(Cortina.fecha_creacion <= fecha_fin)
    
    result = await db.execute(query)
    cortinas = result.scalars().all()
    
    # Calculate basic statistics
    total_cortinas = len(cortinas)
    if total_cortinas == 0:
        return {
            "total_cortinas": 0,
            "costo_promedio": 0,
            "disenos_populares": [],
            "estado_distribucion": {}
        }
    
    # Calculate average cost
    costo_total = sum(c.costo_total for c in cortinas)
    costo_promedio = costo_total / total_cortinas
    
    # Count designs
    disenos_count = {}
    for cortina in cortinas:
        diseno_nombre = cortina.diseno.nombre
        disenos_count[diseno_nombre] = disenos_count.get(diseno_nombre, 0) + 1
    
    # Get most popular designs
    disenos_populares = sorted(
        disenos_count.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    # Calculate status distribution
    estado_distribucion = {}
    for cortina in cortinas:
        estado_distribucion[cortina.estado] = estado_distribucion.get(cortina.estado, 0) + 1
    
    return {
        "total_cortinas": total_cortinas,
        "costo_promedio": round(costo_promedio, 2),
        "disenos_populares": [
            {"diseno": nombre, "cantidad": cantidad}
            for nombre, cantidad in disenos_populares
        ],
        "estado_distribucion": estado_distribucion
    }

async def get_cortinas_by_diseno(
    db: AsyncSession,
    diseno_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Cortina]:
    """
    Retrieve all curtains made with a specific design.
    
    This function is useful for:
    1. Analyzing design popularity
    2. Tracking material usage patterns
    3. Calculating design-specific statistics
    
    Args:
        db: Async database session
        diseno_id: ID of the design to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[Cortina]: List of curtains using the specified design
    """
    query = (
        select(Cortina)
        .options(
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.tipo_insumo),
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.referencia),
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.color)
        )
        .where(Cortina.diseno_id == diseno_id)
        .order_by(Cortina.fecha_creacion.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_consumo_materiales(
    db: AsyncSession,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
) -> List[Dict[str, any]]:
    """
    Calculate material consumption statistics for curtain production.
    
    This function helps with:
    1. Inventory planning
    2. Identifying most used materials
    3. Cost analysis
    4. Trend analysis
    
    Args:
        db: Async database session
        fecha_inicio: Optional start date
        fecha_fin: Optional end date
        
    Returns:
        List[Dict]: Material consumption statistics
    """
    # First get all relevant curtains
    query = (
        select(Cortina)
        .options(
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.tipo_insumo),
            selectinload(Cortina.diseno)
            .selectinload(Diseno.tipos_insumo)
            .joinedload(DisenoTipoInsumo.referencia)
        )
    )
    
    if fecha_inicio:
        query = query.where(Cortina.fecha_creacion >= fecha_inicio)
    if fecha_fin:
        query = query.where(Cortina.fecha_creacion <= fecha_fin)
    
    result = await db.execute(query)
    cortinas = result.scalars().all()
    
    # Calculate consumption for each material
    consumo = {}
    for cortina in cortinas:
        for tipo_insumo_rel in cortina.diseno.tipos_insumo:
            cantidad = (
                tipo_insumo_rel.cantidad_por_metro * 
                (cortina.ancho / 100) * 
                cortina.multiplicador
            )
            
            key = (
                tipo_insumo_rel.tipo_insumo.nombre,
                tipo_insumo_rel.referencia.codigo
            )
            
            if key not in consumo:
                consumo[key] = {
                    "tipo_insumo": tipo_insumo_rel.tipo_insumo.nombre,
                    "referencia": tipo_insumo_rel.referencia.codigo,
                    "cantidad_total": 0,
                    "cortinas_count": 0,
                    "costo_total": 0
                }
            
            consumo[key]["cantidad_total"] += cantidad
            consumo[key]["cortinas_count"] += 1
            consumo[key]["costo_total"] += (
                cantidad * tipo_insumo_rel.referencia.precio_unitario
            )
    
    # Convert to list and calculate averages
    resultado = []
    for stats in consumo.values():
        stats["cantidad_promedio"] = (
            stats["cantidad_total"] / stats["cortinas_count"]
        )
        stats["costo_promedio"] = (
            stats["costo_total"] / stats["cortinas_count"]
        )
        resultado.append(stats)
    
    return sorted(
        resultado,
        key=lambda x: x["cantidad_total"],
        reverse=True
    )