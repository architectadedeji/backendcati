"""Check interview due logic"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.interview import Interview, InterviewRound
from app.models.contact import Contact

async def check_due():
    async with AsyncSessionLocal() as session:
        # Check all interviews
        result = await session.execute(select(Interview))
        interviews = result.scalars().all()
        
        print("All Interviews:")
        print("=" * 80)
        for iv in interviews:
            print(f"ID: {iv.id}, Contact: {iv.contact_id}, Round: {iv.round_number}, "
                  f"Started: {iv.started_at}, Completed: {iv.completed_at}")
        
        print("\n\nAll InterviewRounds:")
        print("=" * 80)
        result = await session.execute(select(InterviewRound))
        rounds = result.scalars().all()
        for ir in rounds:
            print(f"Contact: {ir.contact_id}, Round: {ir.round_number}, Status: {ir.status}, "
                  f"CanStart: {ir.can_start_interview}")
        
        # Check contacts
        print("\n\nContacts:")
        print("=" * 80)
        result = await session.execute(select(Contact).limit(5))
        contacts = result.scalars().all()
        for c in contacts:
            print(f"ID: {c.id}, Name: {c.name}, Status: {c.status}")

asyncio.run(check_due())
