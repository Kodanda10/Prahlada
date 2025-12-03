#!/usr/bin/env python3
"""
Initialize Database Tables
Creates all tables defined in models.py if they don't exist.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import engine
from backend.models import Base

async def init_db():
    """Initialize all database tables."""
    print("🔧 Initializing database tables...")
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables initialized successfully!")
    print(f"   Tables created: {', '.join(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    asyncio.run(init_db())
