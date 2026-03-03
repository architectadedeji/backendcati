#!/usr/bin/env python3
"""Test UserResponse validation."""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.auth import UserResponse

async def test():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        if user:
            print(f"User found: {user.username}, {user.email}")
            print(f"User dict: {vars(user)}")
            try:
                validated = UserResponse.model_validate(user)
                print(f"Validation SUCCESS: {validated}")
            except Exception as e:
                print(f"Validation FAILED: {type(e).__name__}: {e}")
        else:
            print("User not found")

if __name__ == "__main__":
    asyncio.run(test())
