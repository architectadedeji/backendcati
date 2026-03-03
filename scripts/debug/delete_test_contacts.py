#!/usr/bin/env python3
"""Delete the 5 original test contacts"""

import asyncio
import sys
sys.path.insert(0, '/dev-2026/streamcati/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from app.models.contact import Contact

async def main():
    try:
        engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            # Get the 5 test contacts before deletion
            result = await db.execute(select(Contact).where(Contact.id.in_([1, 2, 3, 4, 5])))
            contacts_to_delete = result.scalars().all()
            
            print(f"Deleting {len(contacts_to_delete)} test contacts:")
            for contact in contacts_to_delete:
                print(f"  - ID {contact.id}: {contact.name}")
            
            # Delete them
            await db.execute(delete(Contact).where(Contact.id.in_([1, 2, 3, 4, 5])))
            await db.commit()
            
            # Verify deletion
            result = await db.execute(select(Contact))
            remaining = result.scalars().all()
            
            print(f"\n✅ Deletion complete!")
            print(f"📊 Remaining contacts: {len(remaining)}")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
