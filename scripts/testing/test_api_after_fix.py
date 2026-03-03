#!/usr/bin/env python3
"""Test API endpoints after email field removal and create_contact fix"""

import asyncio
import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys
sys.path.insert(0, '/dev-2026/streamcati/backend')

from app.models.contact import Contact

async def main():
    # Query database directly to ensure contacts exist
    engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        result = await db.execute(select(Contact))
        contacts = result.scalars().all()
        
        print(f"✅ Database query successful")
        print(f"📊 Total contacts in database: {len(contacts)}")
        
        if contacts:
            print("\n📋 Contact list:")
            for contact in contacts:
                print(f"  - ID: {contact.id}, Name: {contact.name}, Serial: {contact.serial_number}, Location: {contact.location}")
        else:
            print("⚠️  No contacts found in database")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
