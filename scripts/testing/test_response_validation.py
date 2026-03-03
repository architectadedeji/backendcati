#!/usr/bin/env python3
"""Test ContactResponse validation"""

import asyncio
import sys
sys.path.insert(0, '/dev-2026/streamcati/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.contact import Contact
from app.schemas.contacts import ContactResponse

async def main():
    try:
        print("Testing ContactResponse validation...")
        
        engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            # Get contacts
            result = await db.execute(select(Contact))
            contacts = result.scalars().all()
            
            print(f"Found {len(contacts)} contacts")
            
            # Test validation
            for contact in contacts:
                print(f"\nValidating contact {contact.id}: {contact.name}")
                try:
                    response = ContactResponse.model_validate(contact)
                    print(f"  ✅ Validated: {response.name} ({response.location})")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
        
        await engine.dispose()
        print("\n✅ ContactResponse validation test complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
