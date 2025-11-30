#!/usr/bin/env python3
"""
Standalone Knowledge Ingestion Script

Bypasses GeminiParserV2 to avoid import hang issues.
Uses only verified working components for data ingestion.
"""
import asyncio
import csv
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import engine, AsyncSessionLocal
from backend import models
from backend.knowledge_store import KnowledgeStore

# Import isolated resolver components (no cognitive dependencies)
exec(open(PROJECT_ROOT / "scripts" / "isolated_resolver.py").read())

async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
    print("✅ Database tables recreated.")

async def ingest_from_csv(csv_path: Path, limit: int = 10):
    """
    Ingest tweets from CSV using standalone resolver.
    """
    # Load CSV
    tweets = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tweets.append(row)
            if len(tweets) >= limit:
                break
    
    print(f"📥 Loaded {len(tweets)} tweets from {csv_path}")
    
    # Initialize components
    await init_db()
    resolver = HybridLocationResolver(enable_semantic=False)
    
    # Process tweets
    async with AsyncSessionLocal() as db_session:
        knowledge_store = KnowledgeStore(db_session)
        
        for row in tweets:
            tweet_id = str(row['tweet_id'])
            text = row['raw_text']
            
            print(f"\n🔄 Processing tweet {tweet_id}...")
            
            # Simple parsing (location only, no cognitive engine)
            location_result, confidence, source = resolver.resolve(text, [])
            
            # Create minimal parsed data
            parsed_data = {
                "tweet_id": tweet_id,
                "text": text,
                "event_type": "अन्य",  # Default event type
                "location": location_result,
                "confidence": confidence,
                "cognitive_view": None,
                "quality_flags": {},
                "word_buckets": []
            }
            
            print(f"   📍 Location: {location_result.get('canonical') if location_result else 'None'}")
            print(f"   🎯 Confidence: {confidence:.2f}")
            
            # Save to knowledge base
            await knowledge_store.save_parsed_tweet(parsed_data)
            
    print(f"\n✅ Ingestion complete! Processed {len(tweets)} tweets.")

def main():
    csv_path = PROJECT_ROOT / "data" / "gold_standard_tweets.csv"
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return
    
    asyncio.run(ingest_from_csv(csv_path, limit=10))

if __name__ == "__main__":
    main()
