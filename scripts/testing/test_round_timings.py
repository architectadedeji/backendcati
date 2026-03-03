#!/usr/bin/env python3
"""Test the round-timings endpoint."""

import asyncio
import httpx
from app.database import engine, Base, AsyncSessionLocal
from app.models.contact import Contact
from sqlalchemy import select

async def test_round_timings():
    """Test the round-timings endpoint."""
    async with AsyncSessionLocal() as session:
        # Get the first contact
        result = await session.execute(select(Contact).limit(1))
        contact = result.scalar_one_or_none()
        
        if not contact:
            print("No contacts found in database")
            return
        
        print(f"Testing with contact {contact.id}: {contact.name}")
        print(f"Contact status: {contact.status}")
        
        # Test the endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/api/interviews/contact/{contact.id}/round-timings/",
                headers={"Authorization": "Bearer admin"}
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body:")
            print(response.json())

if __name__ == "__main__":
    asyncio.run(test_round_timings())
