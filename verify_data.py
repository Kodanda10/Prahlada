
import asyncio
from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent
from sqlalchemy import select, func

async def verify_data():
    async with AsyncSessionLocal() as session:
        # Count total parsed events
        result = await session.execute(select(func.count(ParsedEvent.id)))
        count = result.scalar()
        print(f"Total Parsed Tweets: {count}")

        # Check for word_buckets in a sample
        result = await session.execute(select(ParsedEvent).limit(5))
        events = result.scalars().all()
        
        buckets_found = 0
        for event in events:
            # Check if 'word_buckets' exists in categories JSON
            cats = event.categories
            if isinstance(cats, dict) and ('word_buckets' in cats or 'keywords' in cats):
                buckets = cats.get('word_buckets') or cats.get('keywords')
                if buckets:
                    buckets_found += 1
                    print(f"Tweet {event.id} has buckets: {buckets}")
        
        print(f"Sampled 5 tweets, found buckets in {buckets_found}")

if __name__ == "__main__":
    asyncio.run(verify_data())
