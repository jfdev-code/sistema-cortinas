# app/database.py
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, text, exc
import os

# Remove model imports from here

# Configure Robust Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'sqlite+aiosqlite:///./cortinas.db'
)

# Naming Convention for Database Objects
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Metadata Configuration
metadata = MetaData(naming_convention=NAMING_CONVENTION)

# Declarative Base
Base = declarative_base(metadata=metadata)

def to_dict(self):
    """Convert SQLAlchemy model instance to a dictionary."""
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base.to_dict = to_dict

# Async Engine Creation
try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv('SQL_ECHO', 'False').lower() == 'true',
        future=True,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )
except Exception as db_init_error:
    logger.error(f"Database engine creation failed: {db_init_error}")
    raise

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database Session Dependency Injection

    Provides a transactional database session with:
    - Foreign key support
    - Error handling
    - Automatic resource management
    """
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("PRAGMA foreign_keys=ON"))
            yield session
        except exc.SQLAlchemyError as db_error:
            logger.error(f"Database session error: {db_error}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """
    Comprehensive database initialization method.
    
    Systematic approach to:
    - Drop existing tables
    - Create tables with precise dependency ordering
    - Handle potential initialization errors
    """
    try:
        # Dynamically import models to avoid circular imports
        from .models.tipo_insumo import TipoInsumo
        from .models.referencia_insumo import ReferenciaInsumo
        from .models.color_insumo import ColorInsumo
        from .models.diseno import Diseno, DisenoTipoInsumo
        from .models.inventario_insumo import InventarioInsumo
        from .models.cortina import Cortina

        logger.info("Starting comprehensive database initialization...")
        
        async with engine.begin() as conn:
            # Explicitly enable foreign key support
            await conn.execute(text("PRAGMA foreign_keys=ON"))
            
            # Use a systematic table creation order
            tables_creation_order = [
                TipoInsumo.__table__,     # Foundational type categories
                ReferenciaInsumo.__table__,  # References linked to types
                ColorInsumo.__table__,    # Colors linked to references
                Diseno.__table__,         # Design templates
                DisenoTipoInsumo.__table__,  # Mapping between designs and types
                InventarioInsumo.__table__,  # Inventory tracking
                Cortina.__table__         # Final product representation
            ]
            
            # Drop existing tables systematically
            await conn.run_sync(Base.metadata.drop_all)
            
            # Create tables with explicit ordering
            for table in tables_creation_order:
                try:
                    await conn.run_sync(
                        lambda sync_conn: table.create(sync_conn, checkfirst=True)
                    )
                    logger.info(f"Successfully created table: {table.name}")
                except Exception as table_error:
                    logger.error(f"Error creating table {table.name}: {table_error}")
                    raise
        
        logger.info("Database initialization completed successfully!")
    
    except Exception as init_error:
        logger.error(f"Comprehensive database initialization failed: {init_error}")
        raise

# Additional utility functions
async def test_db_connection() -> bool:
    """Verify database connectivity"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as conn_error:
        logger.error(f"Database connection test failed: {conn_error}")
        return False

async def close_db_connections() -> None:
    """Safely close database connections"""
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully.")
    except Exception as close_error:
        logger.error(f"Error closing database connections: {close_error}")

# Expose key components
__all__ = [
    'Base', 
    'engine', 
    'AsyncSessionLocal', 
    'get_db', 
    'init_db', 
    'close_db_connections',
    'test_db_connection'
]