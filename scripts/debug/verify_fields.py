import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def verify():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT id, name, batch_number, batch_serial_number, study_arm, method FROM contacts WHERE id = 6"))
        row = result.fetchone()
        if row:
            print(f"MySQL Contact 6:")
            print(f"  ID: {row[0]}")
            print(f"  Name: {row[1]}")
            print(f"  Batch Number: {row[2]}")
            print(f"  Batch Serial: {row[3]}")
            print(f"  Study Arm: {row[4]}")
            print(f"  Method: {row[5]}")
        else:
            print("Contact 6 not found!")

asyncio.run(verify())
