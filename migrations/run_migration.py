import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./cortinas.db')

async def run_migration():
    """
    Ejecuta la migración de la base de datos para añadir las columnas de cliente, telefono y email.
    Maneja las particularidades de SQLite y asegura una migración segura y consistente.
    """
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        future=True
    )

    try:
        async with engine.begin() as conn:
            print("\n🚀 Iniciando migración de la base de datos...")

            # Obtenemos la estructura actual usando el nombre correcto de la columna 'name'
            result = await conn.execute(text("PRAGMA table_info(cortinas)"))
            rows = result.fetchall()
            # El índice 1 en PRAGMA table_info corresponde al nombre de la columna
            existing_columns = {row[1] for row in rows}

            # Definimos las columnas a añadir con tipos compatibles con SQLite
            new_columns = [
                ("cliente", "TEXT"),
                ("telefono", "TEXT"),
                ("email", "TEXT")
            ]

            # Añadimos las columnas que faltan
            for column_name, column_type in new_columns:
                if column_name not in existing_columns:
                    try:
                        # Construimos y ejecutamos el ALTER TABLE
                        alter_statement = text(
                            f"ALTER TABLE cortinas ADD COLUMN {column_name} {column_type}"
                        )
                        await conn.execute(alter_statement)
                        print(f"✅ Añadida columna: {column_name}")
                    except Exception as e:
                        print(f"❌ Error al añadir columna {column_name}: {str(e)}")
                        raise
                else:
                    print(f"ℹ️ La columna {column_name} ya existe")

            # Verificamos la estructura final para confirmar los cambios
            print("\n📊 Estructura final de la tabla:")
            print("-" * 60)
            result = await conn.execute(text("PRAGMA table_info(cortinas)"))
            for row in result.fetchall():
                # Los índices 1 y 2 corresponden al nombre y tipo de columna respectivamente
                print(f"Columna: {row[1]:<20} Tipo: {row[2]:<15}")
            print("-" * 60)

            print("\n✨ Migración completada exitosamente!")

    except Exception as e:
        print(f"\n❌ Error crítico durante la migración: {str(e)}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())