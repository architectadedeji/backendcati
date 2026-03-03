import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text

async def verify_migration():
    async with AsyncSessionLocal() as session:
        # Count total contacts
        result = await session.execute(text("SELECT COUNT(*) FROM contacts"))
        count = result.scalar()
        print(f"[INFO] Total contacts in MySQL: {count}")
        
        # Show sample contacts
        result = await session.execute(text("SELECT id, name, email, location FROM contacts LIMIT 5"))
        print("[INFO] Sample contacts:")
        for row in result:
            print(f"  - ID {row[0]}: {row[1]} ({row[3]})")
        
        # Show status breakdown
        result = await session.execute(text("SELECT status, COUNT(*) FROM contacts GROUP BY status"))
        print("[INFO] Contacts by status:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}")

asyncio.run(verify_migration())
