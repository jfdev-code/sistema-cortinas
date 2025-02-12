# populate_database.py
import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC

# Import our models
from app.models.tipo_insumo import TipoInsumo
from app.models.referencia_insumo import ReferenciaInsumo
from app.models.color_insumo import ColorInsumo
from app.models.inventario_insumo import InventarioInsumo
from app.models.diseno import Diseno, DisenoTipoInsumo
from app.models.cortina import Cortina

from app.database import Base, engine, AsyncSessionLocal

def print_status(message, success=True):
    """Prints formatted status messages"""
    symbol = "✓" if success else "✗"
    print(f"{symbol} {message}")

async def clear_table(db: AsyncSession, table_name: str):
    """Safely clears all records from a table using text() for SQL"""
    try:
        await db.execute(text(f"DELETE FROM {table_name}"))
        return True
    except Exception as e:
        print_status(f"Error clearing {table_name}: {str(e)}", False)
        return False

async def create_design_with_materials(
    db: AsyncSession,
    design_data: dict,
    tipos_insumo: dict
) -> Diseno:
    """
    Creates a design with its required material types.
    
    This function implements the correct business logic where:
    1. A design specifies what types of materials it needs
    2. Each material type has an associated quantity per meter
    3. The specific references and colors are chosen later when creating a curtain
    
    Args:
        db: The database session
        design_data: Dictionary containing design information and required materials
        tipos_insumo: Dictionary mapping material type names to their database objects
    """
    # First create the base design
    diseno = Diseno(
        id_diseno=design_data["codigo"],
        nombre=design_data["nombre"],
        descripcion=design_data["descripcion"],
        costo_mano_obra=design_data["costo_mano_obra"],
        complejidad=design_data["complejidad"]
    )
    db.add(diseno)
    # Flush to get the ID before creating relationships
    await db.flush()
    
    # Create relationships for each required material type
    for material in design_data["tipos_insumo"]:
        tipo_insumo_rel = DisenoTipoInsumo(
            diseno_id=diseno.id,
            tipo_insumo_id=tipos_insumo[material["tipo_insumo"]].id,
            cantidad_por_metro=material["cantidad_por_metro"],
            descripcion=material["descripcion"]
        )
        db.add(tipo_insumo_rel)
    
    return diseno

async def populate_database(clean_first=True):
    """Main function to populate the database with test data"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        try:
            if clean_first:
                print("\nLimpiando datos existentes...")
                # Delete in reverse order of dependencies
                await clear_table(db, "cortinas")
                await clear_table(db, "diseno_tipos_insumo")
                await clear_table(db, "disenos")
                await clear_table(db, "inventario_insumos")
                await clear_table(db, "colores_insumo")
                await clear_table(db, "referencias_insumo")
                await clear_table(db, "tipos_insumo")
                await db.commit()
                print_status("Base de datos limpiada exitosamente")

            print("\nCreando datos de prueba...")

            # Create material types first
            tipos_insumo_data = [
                ("Tela", "Telas para cortinas y persianas"),
                ("Screen", "Telas tipo screen para control solar"),
                ("Blackout", "Telas blackout para oscuridad total"),
                ("Riel", "Sistemas de rieles y soportes"),
                ("Cadena", "Sistemas de control manual"),
                ("Motor", "Sistemas de automatización"),
                ("Terminal", "Terminales y acabados decorativos"),
                ("Soporte", "Soportes de pared y techo"),
                ("Cenefa", "Elementos decorativos superiores"),
                ("Componente", "Componentes y accesorios varios")
            ]

            tipos_insumo = {}
            for nombre, desc in tipos_insumo_data:
                tipo = TipoInsumo(nombre=nombre, descripcion=desc)
                db.add(tipo)
                tipos_insumo[nombre] = tipo
            
            await db.flush()
            print_status("Tipos de insumo creados")

            # Create references for each type
            referencias_data = [
                # Telas
                ("Tela", "TEL-001", "Tela Decorativa Premium", 65000),
                ("Tela", "TEL-002", "Tela Decorativa Basic", 45000),
                ("Tela", "TEL-003", "Tela Translúcida", 55000),
                # Screens
                ("Screen", "SCR-001", "Screen 5% Premium", 85000),
                ("Screen", "SCR-002", "Screen 3% Basic", 75000),
                ("Screen", "SCR-003", "Screen 1% Ultra", 95000),
                # Blackouts
                ("Blackout", "BLK-001", "Blackout Premium", 75000),
                ("Blackout", "BLK-002", "Blackout Basic", 55000),
                ("Blackout", "BLK-003", "Blackout Ultra", 95000),
                # Rieles
                ("Riel", "RIL-001", "Riel Manual Basic", 35000),
                ("Riel", "RIL-002", "Riel Manual Premium", 45000),
                ("Riel", "RIL-003", "Riel Motorizado", 85000),
                # Cadenas
                ("Cadena", "CAD-001", "Cadena Plástica", 8000),
                ("Cadena", "CAD-002", "Cadena Metálica", 12000),
                # Motores
                ("Motor", "MOT-001", "Motor Basic", 180000),
                ("Motor", "MOT-002", "Motor Premium", 250000),
                ("Motor", "MOT-003", "Motor Smart", 350000),
                # Terminales
                ("Terminal", "TER-001", "Terminal Basic", 15000),
                ("Terminal", "TER-002", "Terminal Premium", 25000),
                # Soportes
                ("Soporte", "SOP-001", "Soporte Pared Basic", 12000),
                ("Soporte", "SOP-002", "Soporte Techo Premium", 18000)
            ]

            referencias = {}
            for tipo_nombre, codigo, nombre, precio in referencias_data:
                ref = ReferenciaInsumo(
                    tipo_insumo_id=tipos_insumo[tipo_nombre].id,
                    codigo=codigo,
                    nombre=nombre,
                    precio_unitario=precio
                )
                db.add(ref)
                referencias[codigo] = ref
            
            await db.flush()
            print_status("Referencias creadas")

            # Create colors for references that need them
            colores_data = [
                # Colores para telas decorativas
                ("TEL-001", [
                    ("TD-BLA", "Blanco Arena"),
                    ("TD-BEI", "Beige Claro"),
                    ("TD-GRI", "Gris Perla"),
                    ("TD-AZU", "Azul Marino"),
                    ("TD-VER", "Verde Sage")
                ]),
                # Colores para screens
                ("SCR-001", [
                    ("SC-BLA", "Blanco"),
                    ("SC-GRI", "Gris"),
                    ("SC-NEG", "Negro"),
                    ("SC-BEI", "Beige")
                ]),
                # Colores para blackouts
                ("BLK-001", [
                    ("BK-BLA", "Blanco"),
                    ("BK-GRI", "Gris"),
                    ("BK-BEI", "Beige"),
                    ("BK-NEG", "Negro"),
                    ("BK-AZU", "Azul")
                ])
            ]

            colores = {}
            for ref_codigo, color_list in colores_data:
                for codigo, nombre in color_list:
                    color = ColorInsumo(
                        referencia_id=referencias[ref_codigo].id,
                        codigo=codigo,
                        nombre=nombre
                    )
                    db.add(color)
                    colores[codigo] = color

            await db.flush()
            print_status("Colores creados")

            # Create initial inventory
            for color in colores.values():
                inventario = InventarioInsumo(
                    referencia_id=color.referencia_id,
                    color_id=color.id,
                    cantidad=100.0,
                    cantidad_minima=20.0,
                    ubicacion="Bodega Principal",
                    fecha_ultima_entrada=datetime.now(UTC)
                )
                db.add(inventario)

            await db.flush()
            print_status("Inventario inicial creado")

            # Create designs with their required material types
            disenos_data = [
                {
                    "codigo": "BASIC-001",
                    "nombre": "Cortina Enrollable Basic",
                    "descripcion": "Cortina enrollable básica con tela decorativa",
                    "costo_mano_obra": 35000,
                    "complejidad": "bajo",
                    "tipos_insumo": [
                        {
                            "tipo_insumo": "Tela",
                            "cantidad_por_metro": 2.2,
                            "descripcion": "Tela principal para el cuerpo de la cortina"
                        },
                        {
                            "tipo_insumo": "Riel",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Riel superior para mecanismo"
                        },
                        {
                            "tipo_insumo": "Cadena",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Sistema de control manual"
                        },
                        {
                            "tipo_insumo": "Terminal",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Terminal inferior para peso y acabado"
                        }
                    ]
                },
                {
                    "codigo": "PREM-001",
                    "nombre": "Cortina Enrollable Premium",
                    "descripcion": "Cortina enrollable premium con screen",
                    "costo_mano_obra": 50000,
                    "complejidad": "medio",
                    "tipos_insumo": [
                        {
                            "tipo_insumo": "Screen",
                            "cantidad_por_metro": 2.2,
                            "descripcion": "Screen de alta calidad para el cuerpo principal"
                        },
                        {
                            "tipo_insumo": "Riel",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Riel premium para mecanismo"
                        },
                        {
                            "tipo_insumo": "Cadena",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Sistema de control manual premium"
                        },
                        {
                            "tipo_insumo": "Terminal",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Terminal premium para acabado"
                        },
                        {
                            "tipo_insumo": "Cenefa",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Cenefa decorativa superior"
                        }
                    ]
                },
                {
                    "codigo": "AUTO-001",
                    "nombre": "Cortina Enrollable Motorizada",
                    "descripcion": "Cortina enrollable motorizada con blackout",
                    "costo_mano_obra": 120000,
                    "complejidad": "alto",
                    "tipos_insumo": [
                        {
                            "tipo_insumo": "Blackout",
                            "cantidad_por_metro": 2.2,
                            "descripcion": "Blackout de alta calidad"
                        },
                        {
                            "tipo_insumo": "Riel",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Riel motorizado"
                        },
                        {
                            "tipo_insumo": "Motor",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Sistema de motorización"
                        },
                        {
                            "tipo_insumo": "Terminal",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Terminal premium"
                        },
                        {
                            "tipo_insumo": "Cenefa",
                            "cantidad_por_metro": 1.0,
                            "descripcion": "Cenefa decorativa premium"
                        }
                    ]
                }
            ]

            # Create each design with its material requirements
            disenos = {}
            for diseno_info in disenos_data:
                diseno = await create_design_with_materials(db, diseno_info, tipos_insumo)
                disenos[diseno_info["codigo"]] = diseno
                await db.flush()
            
            print_status("Diseños y requerimientos de materiales creados")

            # Create sample curtains
            cortinas_data = [
                {
                    "diseno": "BASIC-001",
                    "ancho": 150.0,
                    "alto": 180.0,
                    "estado": "completada"
                },
                {
                    "diseno": "PREM-001",
                    "ancho": 200.0,
                    "alto": 220.0,
                    "estado": "en_proceso"
                },
                {
                    "diseno": "AUTO-001",
                    "ancho": 250.0,
                    "alto": 240.0,
                    "estado": "pendiente"
                }
            ]

            for cortina_info in cortinas_data:
                cortina = Cortina(
                    diseno_id=disenos[cortina_info["diseno"]].id,
                    ancho=cortina_info["ancho"],
                    alto=cortina_info["alto"],
                    estado=cortina_info["estado"],
                    multiplicador=1,
                    costo_total=100000.0  # Sample cost
                )
                db.add(cortina)

            await db.flush()
            print_status("Cortinas de muestra creadas")

            # Commit all changes
            await db.commit()
            print("\n¡Datos de prueba insertados exitosamente!")

        except Exception as e:
            print("\n¡Datos de prueba insertados exitosamente!")

        except Exception as e:
            print_status(f"Error durante la inserción de datos: {str(e)}", False)
            await db.rollback()
            raise
        finally:
            await db.close()

async def main():
    """Main entry point to handle async execution"""
    if len(sys.argv) > 1 and sys.argv[1] == "--no-clean":
        await populate_database(clean_first=False)
    else:
        await populate_database()

if __name__ == "__main__":
    asyncio.run(main())