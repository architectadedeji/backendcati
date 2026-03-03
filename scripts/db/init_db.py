#!/usr/bin/env python
"""Initialize the database with all tables."""
import asyncio
from app.database import engine, Base
from app.models import *  # noqa: F401, F403


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
