from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Configure engine based on database type
engine_options = {
    "echo": settings.environment == "development",
    "pool_pre_ping": True,
}

# Only add pool settings for MySQL (not supported by SQLite)
if "mysql" in settings.database_url:
    engine_options["pool_size"] = 10
    engine_options["max_overflow"] = 20

engine = create_async_engine(
    settings.database_url,
    **engine_options
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency that yields a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
