import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import MetaData
from app.config import settings  # Ensure settings contains db_url
from app.models.base import Base # Import your SQLAlchemy Base
from app.models import *

async def reset_database(url):
    """Asynchronously drop and recreate all tables defined in the SQLAlchemy Base metadata."""
    engine = create_async_engine(url, echo=True)
    
    # Drop and recreate all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("All tables dropped.")
        
        # await conn.run_sync(Base.metadata.create_all)
        # print("All tables recreated.")

    # Dispose the engine
    await engine.dispose()
    print("Database reset complete.")

if __name__ == '__main__':
    asyncio.run(reset_database(settings.db_url))
