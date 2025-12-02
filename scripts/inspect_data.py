import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal

async def inspect_data():
    async with AsyncSessionLocal() as session:
        print("🔍 Inspecting 'parsed_events' table...")
        
        # Get total count
        result = await session.execute(text("SELECT count(*) FROM parsed_events"))
        total = result.scalar()
        print(f"   Total Rows: {total}")
        
        # Get sample row
        result = await session.execute(text("SELECT tweet_id, word_buckets FROM parsed_events LIMIT 1"))
        row = result.fetchone()
        
        if row:
            print(f"   Sample Tweet ID: {row[0]}")
            print(f"   Sample Word Buckets: {row[1]} (Type: {type(row[1])})")
        else:
            print("   ⚠️  Table is empty!")

        # Check for non-null buckets
        result = await session.execute(text("SELECT count(*) FROM parsed_events WHERE word_buckets IS NOT NULL"))
        not_null = result.scalar()
        print(f"   Rows with word_buckets IS NOT NULL: {not_null}")

if __name__ == "__main__":
    asyncio.run(inspect_data())
