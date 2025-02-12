# app/utils/transaction.py
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def transaction_scope(db: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for handling database transactions safely.
    Ensures all operations either complete successfully or are rolled back.
    
    Args:
        db: Async SQLAlchemy database session
        
    Yields:
        AsyncSession: The database session
        
    Raises:
        Exception: Any exception that occurs during the transaction
    """
    try:
        yield db
        await db.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        await db.rollback()
        logger.error(f"Transaction rolled back due to error: {str(e)}")
        raise