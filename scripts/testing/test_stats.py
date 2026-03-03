"""Test analytics endpoints"""
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.interview import Interview
from app.models.contact import Contact

async def test_stats():
    async with AsyncSessionLocal() as session:
        # Test 1: Count contacts
        print("=" * 50)
        print("TEST 1: Count contacts")
        try:
            result = await session.execute(select(func.count(Contact.id)))
            count = result.scalar() or 0
            print(f"[OK] Total contacts: {count}")
        except Exception as e:
            print(f"[ERROR] Counting contacts: {e}")
        
        # Test 2: Count total interviews
        print("=" * 50)
        print("TEST 2: Count total interviews")
        try:
            result = await session.execute(select(func.count(Interview.id)))
            count = result.scalar() or 0
            print(f"[OK] Total interviews: {count}")
        except Exception as e:
            print(f"[ERROR] Counting interviews: {e}")
        
        # Test 3: Count completed interviews
        print("=" * 50)
        print("TEST 3: Count completed interviews")
        try:
            result = await session.execute(
                select(func.count(Interview.id)).where(Interview.completed_at.isnot(None))
            )
            count = result.scalar() or 0
            print(f"[OK] Completed interviews: {count}")
        except Exception as e:
            print(f"[ERROR] Counting completed: {e}")
        
        # Test 4: Count in-progress interviews
        print("=" * 50)
        print("TEST 4: Count in-progress interviews")
        try:
            result = await session.execute(
                select(func.count(Interview.id)).where(
                    (Interview.started_at.isnot(None)) & (Interview.completed_at.is_(None))
                )
            )
            count = result.scalar() or 0
            print(f"[OK] In-progress interviews: {count}")
        except Exception as e:
            print(f"[ERROR] Counting in-progress: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test_stats())
