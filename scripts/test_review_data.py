import asyncio
import sys
from pathlib import Path
from sqlalchemy import select

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent, EnrichedItem, RawTweet

async def test_review_query():
    print("🧪 Testing Review Data Query...")
    async with AsyncSessionLocal() as session:
        # Simulate get_events query
        query = (
            select(ParsedEvent, RawTweet, EnrichedItem)
            .join(RawTweet, RawTweet.tweet_id == ParsedEvent.tweet_id, isouter=True)
            .join(EnrichedItem, EnrichedItem.tweet_id == ParsedEvent.tweet_id, isouter=True)
            .where(EnrichedItem.tweet_id.isnot(None)) # Filter for enriched ones for testing
            .limit(5)
        )
        
        result = await session.execute(query)
        rows = result.all()
        
        print(f"📊 Found {len(rows)} enriched rows.")
        
        for parsed, raw, enriched in rows:
            print(f"\nTweet ID: {parsed.tweet_id}")
            print(f"   - Parser Event Type: {parsed.event_type}")
            print(f"   - Gemma 3 Event Type: {enriched.event_type}")
            print(f"   - Gemma 3 Themes: {enriched.themes}")
            print(f"   - Gemma 3 Locations: {enriched.location_candidates}")

if __name__ == "__main__":
    asyncio.run(test_review_query())
