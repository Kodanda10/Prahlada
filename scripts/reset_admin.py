import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.models import AdminUser
from backend.auth import get_password_hash
from backend.database import DATABASE_URL

async def reset_admin():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        result = await session.execute(select(AdminUser).where(AdminUser.username == "admin"))
        user = result.scalar_one_or_none()
        
        if user:
            print("Found admin user. Resetting password...")
            user.password_hash = get_password_hash("admin123")
            await session.commit()
            print("Password reset to 'admin123'.")
        else:
            print("Admin user not found. Creating...")
            new_user = AdminUser(
                username="admin",
                password_hash=get_password_hash("admin123"),
                roles=["admin"],
                display_name="Project Dhruv Admin"
            )
            session.add(new_user)
            await session.commit()
            print("Admin user created with password 'admin123'.")

if __name__ == "__main__":
    asyncio.run(reset_admin())
