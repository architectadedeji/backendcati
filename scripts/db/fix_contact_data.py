#!/usr/bin/env python3
"""Fix contact data to match schema requirements"""

import asyncio
import sys
from datetime import datetime
sys.path.insert(0, '/dev-2026/streamcati/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.models.contact import Contact

async def main():
    try:
        print("Fixing contact data...")
        
        engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            # Get all contacts
            result = await db.execute(select(Contact))
            contacts = result.scalars().all()
            
            print(f"Found {len(contacts)} contacts to fix")
            
            # Fix each contact
            for contact in contacts:
                fixed = False
                
                # Fix status - if it's 'not_started', change to 'round_1'
                if contact.status and contact.status not in ['round_1', 'round_2', 'round_3', 'round_4', 'all_rounds_completed']:
                    old_status = contact.status
                    contact.status = 'round_1'
                    print(f"  Contact {contact.id}: status '{old_status}' → '{contact.status}'")
                    fixed = True
                
                # Fix created_at - if None, use current time
                if contact.created_at is None:
                    contact.created_at = datetime.utcnow()
                    print(f"  Contact {contact.id}: created_at None → {contact.created_at}")
                    fixed = True
                
                if fixed:
                    await db.flush()
            
            # Commit all changes
            await db.commit()
            print(f"\n✅ All {len(contacts)} contacts updated successfully")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
