#!/usr/bin/env python3
"""
Test Script: Run Gemma 3 Enrichment on a Single Tweet
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal
from backend.cognitive.gemma3_enrichment import Gemma3EnrichmentService
from backend.models import RawTweet
from sqlalchemy.future import select

async def test_single_tweet(tweet_id: str):
    """Test enrichment on a single tweet."""
    async with AsyncSessionLocal() as session:
        # Fetch the tweet
        result = await session.execute(select(RawTweet).where(RawTweet.tweet_id == tweet_id))
        tweet = result.scalar_one_or_none()
        
        if not tweet:
            print(f"❌ Tweet {tweet_id} not found!")
            return
        
        print(f"📝 Testing enrichment on tweet: {tweet_id}")
        print(f"   Text: {tweet.text}\n")
        
        # Create service and enrich
        service = Gemma3EnrichmentService(session)
        enriched = await service.enrich_tweet(tweet)
        
        if enriched:
            print("✅ Enrichment successful!")
            print(f"\n🎯 Final Output (The Boss):")
            print(f"Domain: {enriched.layers.get('domain', [])}")
            print(f"Occasion: {enriched.layers.get('occasion', [])}")
            print(f"Action: {enriched.layers.get('action', [])}")
            print(f"Relationship: {enriched.layers.get('relationship', [])}")
            print(f"Strategy: {enriched.layers.get('strategy', [])}")
            print(f"Emotion: {enriched.layers.get('emotion', [])}")
            print(f"Audience: {enriched.layers.get('audience', [])}")
            print(f"People: {enriched.people}")
            print(f"Organizations: {enriched.organizations}")
            print(f"Locations: {enriched.location_candidates}")
            print(f"Schemes: {enriched.schemes}")
            print(f"Event: {enriched.event_type}")
            print(f"Confidence: {enriched.confidence_score}")
            
            print(f"\nNotes: {enriched.notes}")
            
            # Save it
            session.add(enriched)
            await session.commit()
            print(f"\n💾 Saved to database!")
        else:
            print("❌ Enrichment failed!")

if __name__ == "__main__":
    tweet_id = sys.argv[1] if len(sys.argv) > 1 else "1893869785772953917"
    asyncio.run(test_single_tweet(tweet_id))
