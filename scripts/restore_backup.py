#!/usr/bin/env python3
"""
Restore parsed events from JSONL backup to PostgreSQL database.
Simple version that handles schema properly.
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent, RawTweet
from sqlalchemy import select

async def restore_from_backup(backup_file: str):
    """Restore parsed events from JSONL backup."""
    print(f"Reading backup from {backup_file}...")
    
    with open(backup_file, 'r') as f:
        lines = f.readlines()
    
    print(f"Found {len(lines)} records to restore")
    
    async with AsyncSessionLocal() as session:
        restored = 0
        skipped = 0
        errors = 0
        
        for i, line in enumerate(lines):
            try:
                data = json.loads(line.strip())
                tweet_id = data.get('tweet_id') or data.get('id')
                
                if not tweet_id:
                    errors += 1
                    continue
                
                # Check if already exists
                existing = await session.execute(
                    select(ParsedEvent).where(ParsedEvent.tweet_id == tweet_id)
                )
                if existing.scalar_one_or_none():
                    skipped += 1
                    continue
                
                # Create ParsedEvent - id must be set to tweet_id
                event = ParsedEvent(
                    id=str(tweet_id),  # Primary key must be set
                    tweet_id=str(tweet_id),
                    event_type=data.get('event_type'),
                    locations=data.get('locations') if data.get('locations') != 'null' else None,
                    people_mentioned=data.get('people_mentioned', []) or [],
                    schemes_mentioned=data.get('schemes_mentioned', []) or [],
                    word_buckets=data.get('word_buckets'),
                    categories=data.get('categories') if isinstance(data.get('categories'), dict) else {},
                    gemini_metadata=data.get('gemini_metadata') if isinstance(data.get('gemini_metadata'), dict) else {},
                    overall_confidence=float(data.get('overall_confidence', 0.0)),
                    cognitive_view=data.get('cognitive_view') if isinstance(data.get('cognitive_view'), dict) else None,
                    review_status=data.get('review_status', 'pending'),
                    needs_review=bool(data.get('needs_review', False)),
                    final_data=data.get('final_data') if isinstance(data.get('final_data'), dict) else None,
                    parsed_at=datetime.now()
                )
                session.add(event)
                
                # Create stub RawTweet if needed
                raw_exists = await session.execute(
                    select(RawTweet).where(RawTweet.tweet_id == str(tweet_id))
                )
                if not raw_exists.scalar_one_or_none():
                    raw_tweet = RawTweet(
                        tweet_id=str(tweet_id),
                        text=data.get('text', ''),
                        processing_status='processed',
                        created_at=datetime.now()
                    )
                    session.add(raw_tweet)
                
                restored += 1
                
                # Commit every 50 records
                if restored % 50 == 0:
                    await session.commit()
                    print(f"Progress: {restored}/{len(lines)} records restored...")
                    
            except Exception as e:
                errors += 1
                if errors < 10:  # Only print first 10 errors
                    print(f"Error on line {i+1}: {e}")
                await session.rollback()
                continue
        
        # Final commit
        try:
            await session.commit()
        except Exception as e:
            print(f"Final commit error: {e}")
            await session.rollback()
        
        print(f"\n✅ Restore complete!")
        print(f"   Restored: {restored}")
        print(f"   Skipped (already exists): {skipped}")
        print(f"   Errors: {errors}")

if __name__ == "__main__":
    backup_file = sys.argv[1] if len(sys.argv) > 1 else "data/backup_parsed_events.jsonl"
    asyncio.run(restore_from_backup(backup_file))
