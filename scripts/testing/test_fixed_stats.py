"""Test fixed interview statistics"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.interview import Interview, InterviewRound

async def test():
    async with AsyncSessionLocal() as session:
        print("Testing Fixed Interview Statistics")
        print("=" * 70)
        
        for round_num in [1, 2, 3, 4]:
            # Due interviews from InterviewRound without completed Interview
            due_result = await session.execute(
                select(func.count(InterviewRound.id)).where(
                    (InterviewRound.round_number == round_num) &
                    ~select(Interview.id).where(
                        (Interview.contact_id == InterviewRound.contact_id) &
                        (Interview.round_number == InterviewRound.round_number) &
                        (Interview.completed_at.isnot(None))
                    ).correlate(InterviewRound).exists()
                )
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

            print(f"Round {round_num}: {due} due, {completed} completed")

        # Total due
        total_due_result = await session.execute(
            select(func.count(InterviewRound.id)).where(
                ~select(Interview.id).where(
                    (Interview.contact_id == InterviewRound.contact_id) &
                    (Interview.round_number == InterviewRound.round_number) &
                    (Interview.completed_at.isnot(None))
                ).correlate(InterviewRound).exists()
            )
        )
        total_due = total_due_result.scalar() or 0
        print(f"Total due: {total_due}")

        # Total completed
        total_completed_result = await session.execute(
            select(func.count(Interview.id)).where(Interview.completed_at.isnot(None))
        )
        total_completed = total_completed_result.scalar() or 0
        print(f"Total completed: {total_completed}")

asyncio.run(test())
