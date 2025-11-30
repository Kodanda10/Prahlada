import asyncio
import os
import sys
from sqlalchemy import select
from passlib.context import CryptContext

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database import AsyncSessionLocal
from backend.models import AdminUser
from backend.auth import get_password_hash

async def ensure_admin():
    print("Connecting to DB...")
    
    async with AsyncSessionLocal() as session:
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        print(f"Checking for user: {username}")
        result = await session.execute(select(AdminUser).where(AdminUser.username == username))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User {username} already exists.")
            # Optional: Update password to ensure it matches env
            user.password_hash = get_password_hash(password)
            await session.commit()
            print("Password updated to match environment.")
        else:
            print(f"Creating user {username}...")
            new_user = AdminUser(
                username=username,
                password_hash=get_password_hash(password),
                roles=["admin"],
                display_name="Admin User",
                is_active=True
            )
            session.add(new_user)
            await session.commit()
            print(f"User {username} created successfully.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(ensure_admin())
