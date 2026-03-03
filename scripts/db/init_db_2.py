#!/usr/bin/env python
"""Initialize db_2.sqlite3 database with all tables."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import *  # noqa: F401, F403


async def init_db_2():
    """Create all tables in db_2.sqlite3."""
    engine = create_async_engine("sqlite+aiosqlite:///./db_2.sqlite3", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ db_2.sqlite3 created with all tables")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db_2())
