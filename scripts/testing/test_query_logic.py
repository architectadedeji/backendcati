#!/usr/bin/env python3
"""Test the list_contacts endpoint directly"""

import asyncio
import sys
sys.path.insert(0, '/dev-2026/streamcati/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.contact import Contact

async def main():
    try:
        print("Testing contacts query logic...")
        
        engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            # Build query
            query = select(Contact)
            
            print("Executing query...")
            count_result = await db.execute(query)
            all_contacts = count_result.scalars().all()
            total = len(all_contacts)
            
            print(f"Total contacts: {total}")
            print(f"Contacts: {all_contacts}")
            
            # Test pagination
            skip = 0
            limit = 10
            contacts = all_contacts[skip:skip + limit]
            
            print(f"\nPaginated contacts ({skip}:{skip+limit}): {len(contacts)}")
            for contact in contacts:
                print(f"  - {contact.id}: {contact.name}")
        
        await engine.dispose()
        print("\n✅ Query logic test successful")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
