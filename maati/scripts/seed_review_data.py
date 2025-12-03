import asyncio
import sys
import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import engine, AsyncSessionLocal
from backend.models import RawTweet, ParsedEvent

async def seed_data():
    print("🌱 Seeding sample review data...")
    
    async with AsyncSessionLocal() as session:
        # 1. Create a RawTweet
        tweet_id = "1893895288290500999"
        raw_tweet = RawTweet(
            tweet_id=tweet_id,
            text="CM Baghel announced new irrigation scheme for farmers in Siltara village of Raipur district. #Chhattisgarh #Agriculture",
            created_at=datetime.datetime.utcnow(),
            author_handle="test_handle",
            processing_status="processed",
            fetched_at=datetime.datetime.utcnow(),
            processed_at=datetime.datetime.utcnow()
        )
        
        # 2. Create a ParsedEvent
        parsed_event = ParsedEvent(
            id=tweet_id,
            tweet_id=tweet_id,
            categories={
                "event_type": "Announcement",
                "location": {
                    "district": "Raipur",
                    "block": "Dharsiwa",
                    "village": "Siltara"
                },
                "people": ["Bhupesh Baghel"],
                "schemes": ["Irrigation Scheme"],
                "word_buckets": ["Agriculture", "Development", "Welfare"],
                "communities": ["Farmers"]
            },
            event_type="Announcement",
            # locations=["Raipur", "Siltara"], # Commented out due to DB type mismatch (JSONB vs ARRAY)
            people_mentioned=["Bhupesh Baghel"],
            schemes_mentioned=["Irrigation Scheme"],
            word_buckets=["Agriculture", "Development", "Welfare"],
            overall_confidence=0.95,
            needs_review=True,
            review_status="pending",
            parsed_at=datetime.datetime.utcnow()
        )

        # Check if exists
        existing_tweet = await session.get(RawTweet, tweet_id)
        if existing_tweet:
            print(f"Tweet {tweet_id} already exists. Deleting old data...")
            await session.delete(existing_tweet)
            existing_event = await session.get(ParsedEvent, tweet_id)
            if existing_event:
                await session.delete(existing_event)
            await session.commit()

        session.add(raw_tweet)
        session.add(parsed_event)
        await session.commit()
        
    print(f"✅ Sample tweet {tweet_id} seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
