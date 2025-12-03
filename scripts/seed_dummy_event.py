import asyncio
import datetime
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.models import ParsedEvent, EnrichedItem, RawTweet
from backend.database import DATABASE_URL

async def seed():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        tweet_id = f"dummy_{uuid.uuid4().hex[:8]}"
        
        # 1. Raw Tweet
        raw = RawTweet(
            tweet_id=tweet_id,
            text="माननीय मुख्यमंत्री जी ने आज रायपुर में किसान सम्मान निधि योजना के तहत किसानों को राशि वितरित की। #Farmers #Raipur",
            created_at=datetime.datetime.utcnow(),
            processing_status="processed"
        )
        session.add(raw)

        # 2. Parsed Event (Parser V2)
        parsed = ParsedEvent(
            id=tweet_id,
            tweet_id=tweet_id,
            event_type="distribution",
            categories={
                "location": {"canonical": "Raipur", "type": "District"},
                "schemes": ["Kisan Samman Nidhi"],
                "people": ["Chief Minister"]
            },
            review_status="pending",
            needs_review=True,
            parsed_at=datetime.datetime.utcnow()
        )
        session.add(parsed)

        # 3. Enriched Item (LLM Engine)
        enriched = EnrichedItem(
            tweet_id=tweet_id,
            event_type="Scheme Distribution",
            location_candidates=[
                {"name": "Raipur", "type": "District", "confidence": 0.95},
                {"name": "Chhattisgarh", "type": "State", "confidence": 0.99}
            ],
            schemes=["PM Kisan Samman Nidhi"],
            people=["Bhupesh Baghel"], 
            confidence_score=0.92,
            enriched_at=datetime.datetime.utcnow()
        )
        session.add(enriched)

        await session.commit()
        print(f"Seeded dummy event: {tweet_id}")

if __name__ == "__main__":
    asyncio.run(seed())
