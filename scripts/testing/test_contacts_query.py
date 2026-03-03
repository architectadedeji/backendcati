#!/usr/bin/env python
"""Test contacts endpoint."""
import asyncio
import sqlite3
from app.database import get_db, engine, AsyncSessionLocal
from app.models.contact import Contact
from sqlalchemy import select


async def test_contacts():
    """Test that we can query contacts."""
    async with AsyncSessionLocal() as session:
        # Query contacts
        result = await session.execute(select(Contact))
        contacts = result.scalars().all()
        
        print(f"✅ Contacts query successful")
        print(f"📊 Total contacts: {len(contacts)}\n")
        
        if contacts:
            print("Sample contacts:")
            for contact in contacts[:5]:
                print(f"  - {contact.id}: {contact.name} ({contact.location})")
        else:
            print("❌ No contacts found!")


if __name__ == "__main__":
    asyncio.run(test_contacts())
