from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)

from .config import settings


DB_URI = settings.db_url

engine = create_async_engine(
    DB_URI,
    echo=False,
    pool_pre_ping=True,  # Check if connection is alive before using
    # pool_size=10,  # Set the size of the connection pool
    # max_overflow=10,  # How many additional connections can be created beyond pool_size
    # pool_timeout=30,  # Timeout in seconds for getting a connection from the pool
    # pool_recycle=1800,  # Recycle connections after 30 minutes
)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

print(DB_URI)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_async_connection():
    async with engine.connect() as conn:
        yield conn