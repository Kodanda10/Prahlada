#!/usr/bin/env python3
"""
Ingest parsed tweets from data/parsed_tweets_v8.jsonl into PostgreSQL.

Usage:
    # From host machine
    docker-compose exec backend python scripts/ingest_v8_to_postgres.py
    
    # Or directly if running backend locally
    python scripts/ingest_v8_to_postgres.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://dhruv:dhruv123@localhost:5432/dhruv_db"
)

# Convert SQLAlchemy URL to asyncpg format
ASYNCPG_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def ingest():
    """Main ingestion function."""
    data_file = Path(__file__).parent.parent / "data" / "parsed_tweets_v8.jsonl"
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    print(f"📂 Reading from: {data_file}")
    
    # Connect to database
    conn = await asyncpg.connect(ASYNCPG_URL)
    print("✅ Connected to PostgreSQL")
    
    try:
        # Read all tweets
        tweets = []
        with open(data_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    tweets.append(json.loads(line))
        
        print(f"📊 Found {len(tweets)} tweets to ingest")
        
        # Track stats
        raw_inserted = 0
        parsed_inserted = 0
        enriched_inserted = 0
        
        for i, tweet in enumerate(tweets):
            tweet_id = tweet.get("tweet_id")
            raw_text = tweet.get("raw_text", "")
            created_at = tweet.get("created_at")
            parsed_data = tweet.get("parsed_data_v8", {})
            metadata = tweet.get("metadata_v8", {})
            
            if not tweet_id:
                continue
            
            # Parse date
            try:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    created_at = datetime.utcnow()
            except:
                created_at = datetime.utcnow()
            
            # 1. Insert into raw_tweets
            try:
                await conn.execute("""
                    INSERT INTO raw_tweets (tweet_id, text, created_at, processing_status, fetched_at)
                    VALUES ($1, $2, $3, 'processed', NOW())
                    ON CONFLICT (tweet_id) DO NOTHING
                """, tweet_id, raw_text, created_at)
                raw_inserted += 1
            except Exception as e:
                pass  # Skip duplicates
            
            # 2. Insert into parsed_events
            try:
                event_type = parsed_data.get("event_type", "अन्य")
                locations = parsed_data.get("location")
                people = parsed_data.get("people_canonical") or parsed_data.get("people_mentioned") or []
                schemes = parsed_data.get("schemes_mentioned") or []
                word_buckets = parsed_data.get("word_buckets") or []
                confidence = parsed_data.get("confidence", 0.0)
                needs_review = parsed_data.get("needs_review", True)
                review_status = parsed_data.get("review_status", "pending")
                
                await conn.execute("""
                    INSERT INTO parsed_events (
                        id, tweet_id, categories, gemini_metadata, 
                        event_type, locations, people_mentioned, schemes_mentioned, word_buckets,
                        overall_confidence, needs_review, review_status, parsed_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
                    ON CONFLICT (tweet_id) DO UPDATE SET
                        categories = EXCLUDED.categories,
                        event_type = EXCLUDED.event_type,
                        overall_confidence = EXCLUDED.overall_confidence
                """, 
                    tweet_id,  # id
                    tweet_id,  # tweet_id
                    json.dumps(parsed_data),  # categories
                    json.dumps(metadata),  # gemini_metadata
                    event_type,
                    json.dumps(locations) if locations else None,
                    people if people else None,
                    schemes if schemes else None,
                    word_buckets if word_buckets else None,
                    confidence,
                    needs_review,
                    review_status
                )
                parsed_inserted += 1
            except Exception as e:
                print(f"⚠️ Error inserting parsed_event {tweet_id}: {e}")
            
            # 3. Insert into enriched_items
            try:
                themes = parsed_data.get("word_buckets") or parsed_data.get("communities") or []
                communities = parsed_data.get("communities") or []
                organizations = parsed_data.get("organizations") or []
                target_groups = parsed_data.get("target_groups") or []
                sentiment = "Neutral"  # Default
                
                await conn.execute("""
                    INSERT INTO enriched_items (
                        tweet_id, themes, event_type, sentiment,
                        location_candidates, schemes, communities, people, organizations,
                        confidence_score, model_version, enriched_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                    ON CONFLICT (tweet_id) DO UPDATE SET
                        themes = EXCLUDED.themes,
                        event_type = EXCLUDED.event_type
                """,
                    tweet_id,
                    json.dumps(themes),  # themes
                    event_type,
                    sentiment,
                    json.dumps(locations) if locations else None,  # location_candidates
                    schemes if schemes else None,
                    communities if communities else None,
                    people if people else None,
                    organizations if organizations else None,
                    confidence,
                    "gemini-parser-v8"
                )
                enriched_inserted += 1
            except Exception as e:
                print(f"⚠️ Error inserting enriched_item {tweet_id}: {e}")
            
            # Progress
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(tweets)}...")
        
        print(f"\n✅ Ingestion complete!")
        print(f"   Raw tweets: {raw_inserted}")
        print(f"   Parsed events: {parsed_inserted}")
        print(f"   Enriched items: {enriched_inserted}")
        
        # Verify counts
        raw_count = await conn.fetchval("SELECT COUNT(*) FROM raw_tweets")
        parsed_count = await conn.fetchval("SELECT COUNT(*) FROM parsed_events")
        enriched_count = await conn.fetchval("SELECT COUNT(*) FROM enriched_items")
        
        print(f"\n📊 Database totals:")
        print(f"   raw_tweets: {raw_count}")
        print(f"   parsed_events: {parsed_count}")
        print(f"   enriched_items: {enriched_count}")
        
    finally:
        await conn.close()
        print("🔌 Connection closed")


if __name__ == "__main__":
    asyncio.run(ingest())
