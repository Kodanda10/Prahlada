import asyncio
import sys
from pathlib import Path
from sqlalchemy import func, select

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal
from backend.models import RawTweet, EnrichedItem

async def check_status():
    async with AsyncSessionLocal() as session:
        # Count Total Tweets
        result = await session.execute(select(func.count(RawTweet.tweet_id)))
        total_tweets = result.scalar()
        
        # Count Enriched Tweets
        result = await session.execute(select(func.count(EnrichedItem.tweet_id)))
        enriched_count = result.scalar()
        
        # Calculate Pending
        pending = total_tweets - enriched_count
        progress = (enriched_count / total_tweets * 100) if total_tweets > 0 else 0
        
        print(f"📊 Enrichment Status:")
        print(f"   - Total Tweets: {total_tweets}")
        print(f"   - Enriched (Gemma 3): {enriched_count}")
        print(f"   - Pending: {pending}")
        print(f"   - Progress: {progress:.2f}%")

if __name__ == "__main__":
    asyncio.run(check_status())
