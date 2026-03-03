#!/usr/bin/env python3
"""Test the API endpoint for multiple contacts with different statuses."""

import sys
sys.path.insert(0, '.')

import requests
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.contact import Contact
import asyncio

async def test_multiple_contacts():
    try:
        # First, login to get a token
        login_url = "http://localhost:8000/api/auth/login/"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post(login_url, json=login_data)
        
        if login_response.status_code != 200:
            print(f"Login Error: {login_response.json()}")
            return
        
        token = login_response.json().get("token")
        print(f"✅ Authenticated\n")
        
        # Get contacts from database with different statuses
        engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3')
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Contact).limit(5))
            contacts = result.scalars().all()
            
            for contact in contacts:
                print(f"\nContact ID {contact.id}: {contact.name}")
                print(f"  Status: {contact.status}")
                
                # Test the endpoint
                url = f"http://localhost:8000/api/interviews/contact/{contact.id}/round-timings/"
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Round Timings:")
                    for timing in data.get('round_timings', []):
                        status_icon = "✅" if timing['canStart'] else "⏳"
                        print(f"    {status_icon} Round {timing['roundNumber']}: {timing['status']} - {timing['message']}")
                else:
                    print(f"  Error: {response.status_code}")
        
        await engine.dispose()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_multiple_contacts())
