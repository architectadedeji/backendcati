#!/usr/bin/env python3
"""Delete admin user."""
import asyncio
from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models.user import User

async def delete_admin():
    async with AsyncSessionLocal() as db:
        await db.execute(delete(User).where(User.username == "admin"))
        await db.commit()
        print("Admin user deleted")

if __name__ == "__main__":
    asyncio.run(delete_admin())
