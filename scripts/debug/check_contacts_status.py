"""Check contacts and their status"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.contact import Contact
from app.models.interview import Interview, InterviewRound

async def check():
    async with AsyncSessionLocal() as session:
        # Get all contacts and their interview rounds
        result = await session.execute(select(Contact))
        contacts = result.scalars().all()
        
        print("Contacts and their status/rounds:")
        print("=" * 100)
        print(f"{'ID':<4} {'Name':<25} {'Status':<12} {'Round1':<8} {'Round2':<8} {'Round3':<8} {'Round4':<8}")
        print("-" * 100)
        
        for contact in contacts:
            # Get interview rounds for this contact
            ir_result = await session.execute(
                select(InterviewRound).where(InterviewRound.contact_id == contact.id)
            )
            rounds = ir_result.scalars().all()
            
            round_dict = {r.round_number: r.status for r in rounds}
            r1 = round_dict.get(1, 'N/A')
            r2 = round_dict.get(2, 'N/A')
            r3 = round_dict.get(3, 'N/A')
            r4 = round_dict.get(4, 'N/A')
            
            print(f"{contact.id:<4} {contact.name[:24]:<25} {contact.status:<12} {r1:<8} {r2:<8} {r3:<8} {r4:<8}")

asyncio.run(check())
