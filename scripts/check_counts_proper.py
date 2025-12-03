import asyncio
import sys
from pathlib import Path
from sqlalchemy import func, select

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent, EnrichedItem

async def check_counts():
    async with AsyncSessionLocal() as session:
        # Count Parsed Events (Gemma 2)
        result = await session.execute(select(func.count(ParsedEvent.tweet_id)))
        parsed_count = result.scalar()
        
        # Count Enriched Items (Gemma 3)
        result = await session.execute(select(func.count(EnrichedItem.tweet_id)))
        enriched_count = result.scalar()
        
        print(f"📊 Database Counts:")
        print(f"   - Parsed Events (Gemma 2): {parsed_count}")
        print(f"   - Enriched Items (Gemma 3): {enriched_count}")

if __name__ == "__main__":
    asyncio.run(check_counts())
