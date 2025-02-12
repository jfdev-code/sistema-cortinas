# app/utils/database_utils.py
from sqlalchemy import inspect, MetaData
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def verify_table_exists(engine, table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        engine: SQLAlchemy engine instance
        table_name: Name of the table to check
        
    Returns:
        bool: True if table exists, False otherwise
    """
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def safe_init_tables(engine, base, metadata: MetaData):
    """
    Safely initialize database tables, handling existing tables appropriately.
    
    Args:
        engine: SQLAlchemy engine instance
        base: SQLAlchemy declarative base
        metadata: SQLAlchemy MetaData instance
    """
    try:
        # Create tables that don't exist
        for table_name, table in metadata.tables.items():
            if not verify_table_exists(engine, table_name):
                logger.info(f"Creating table: {table_name}")
                table.create(engine, checkfirst=True)
            else:
                logger.info(f"Table already exists: {table_name}")
                
    except Exception as e:
        logger.error(f"Error initializing tables: {str(e)}")
        raise

def verify_database_integrity(engine, base):
    """
    Verify database structure matches the models.
    
    Args:
        engine: SQLAlchemy engine instance
        base: SQLAlchemy declarative base
    
    Returns:
        list: List of any discrepancies found
    """
    inspector = inspect(engine)
    discrepancies = []
    
    # Check each model
    for table_name, table in base.metadata.tables.items():
        # Verify table exists
        if not verify_table_exists(engine, table_name):
            discrepancies.append(f"Missing table: {table_name}")
            continue
            
        # Get actual columns
        actual_columns = {col['name']: col for col in inspector.get_columns(table_name)}
        
        # Check each expected column
        for column in table.columns:
            if column.name not in actual_columns:
                discrepancies.append(
                    f"Missing column: {table_name}.{column.name}"
                )
    
    return discrepancies

def setup_database(engine, base, metadata: MetaData):
    """
    Complete database setup routine including verification.
    
    Args:
        engine: SQLAlchemy engine instance
        base: SQLAlchemy declarative base
        metadata: SQLAlchemy MetaData instance
    """
    logger.info("Starting database setup...")
    
    # Initialize tables
    safe_init_tables(engine, base, metadata)
    
    # Verify integrity
    discrepancies = verify_database_integrity(engine, base)
    
    if discrepancies:
        logger.warning("Database verification found issues:")
        for issue in discrepancies:
            logger.warning(f"  - {issue}")
    else:
        logger.info("Database verification passed successfully")