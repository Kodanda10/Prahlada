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
    print("🚀 Starting count check...")
    async with AsyncSessionLocal() as session:
        # Count Gemma 2 data (ParsedEvent)
        result = await session.execute(select(func.count(ParsedEvent.tweet_id)))
        gemma2_count = result.scalar()
        
        # Count Gemma 3 data (EnrichedItem)
        result = await session.execute(select(func.count(EnrichedItem.tweet_id)))
        gemma3_count = result.scalar()
        
        print(f"📊 Data Integrity Check:")
        print(f"   - Gemma 2 (parsed_events): {gemma2_count} records")
        print(f"   - Gemma 3 (enriched_items): {gemma3_count} records")
        
        if gemma2_count > 0:
            print("✅ Gemma 2 data is SAFE.")
        else:
            print("⚠️  Gemma 2 data count is ZERO!")

if __name__ == "__main__":
    asyncio.run(check_counts())
