"""Test contact status-based interview statistics"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.contact import Contact
from app.models.interview import Interview

async def test():
    async with AsyncSessionLocal() as session:
        print("Interview Statistics (based on Contact Status)")
        print("=" * 70)
        
        # Due by round (from contact status)
        for round_num in [1, 2, 3, 4]:
            due_result = await session.execute(
                select(func.count(Contact.id)).where(Contact.status == f'round_{round_num}')
            )
            due = due_result.scalar() or 0
            
            # Completed
            completed_result = await session.execute(
                select(func.count(Interview.id)).where(
                    (Interview.round_number == round_num) &
                    (Interview.completed_at.isnot(None))
                )
            )
            completed = completed_result.scalar() or 0
            
            print(f"Round {round_num}: {due} due (by status), {completed} completed")

        # Total due
        all_rounds_result = await session.execute(
            select(func.count(Contact.id))
        )
        total_contacts = all_rounds_result.scalar() or 0
        
        # Total completed
        total_completed_result = await session.execute(
            select(func.count(Interview.id)).where(Interview.completed_at.isnot(None))
        )
        total_completed = total_completed_result.scalar() or 0
        
        print(f"\nTotal Contacts: {total_contacts}")
        print(f"Total Completed Interviews: {total_completed}")
        print(f"Total Due Interviews: {total_contacts - total_completed}")

asyncio.run(test())
