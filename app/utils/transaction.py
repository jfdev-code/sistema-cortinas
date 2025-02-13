# app/utils/transaction.py
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def transaction_scope(session: AsyncSession):
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Transaction rolled back due to error: {str(e)}")
        raise