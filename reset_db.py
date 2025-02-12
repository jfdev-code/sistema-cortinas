# reset_db.py
import asyncio
from app.database import Base, engine

async def reset_database():
    """
    Resets the database by dropping all tables and recreating them.
    This gives us a clean slate for populating test data.
    """
    print("Resetting database...")
    async with engine.begin() as conn:
        # Drop all existing tables
        await conn.run_sync(Base.metadata.drop_all)
        print("✓ All tables dropped")
        
        # Recreate all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✓ All tables recreated")
    
    print("Database reset complete!")

if __name__ == "__main__":
    asyncio.run(reset_database())