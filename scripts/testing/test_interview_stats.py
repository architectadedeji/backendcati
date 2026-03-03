"""Test interview statistics endpoint"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.interview import Interview

async def test_interview_stats():
    async with AsyncSessionLocal() as session:
        # Test: Count interviews by round and completion
        print("Interview Statistics Test")
        print("=" * 60)

        for round_num in [1, 2, 3, 4]:
            # Due (not completed)
            due_result = await session.execute(
                select(func.count(Interview.id)).where(
                    (Interview.round_number == round_num) &
                    (Interview.completed_at.is_(None))
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
            select(func.count(Interview.id)).where(Interview.completed_at.is_(None))
        )
        total_due = total_due_result.scalar() or 0
        print(f"Total due interviews: {total_due}")

        # Total completed
        total_completed_result = await session.execute(
            select(func.count(Interview.id)).where(Interview.completed_at.isnot(None))
        )
        total_completed = total_completed_result.scalar() or 0
        print(f"Total completed interviews: {total_completed}")

asyncio.run(test_interview_stats())
