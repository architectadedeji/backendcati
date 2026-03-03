"""CLI script to seed initial admin user."""
import asyncio
from sqlalchemy import select
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.user import User
from app.utils.auth import hash_password


async def seed_admin():
    """Create an admin user if it doesn't exist."""
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            phone="+1234567890",
        )
        
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        print(f"✅ Admin user created successfully!")
        print(f"   ID: {admin.id}")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print()
        print("You can now login with:")
        print("   Username: admin")
        print("   Password: admin123")


if __name__ == "__main__":
    asyncio.run(seed_admin())
