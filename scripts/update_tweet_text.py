#!/usr/bin/env python3
"""Update raw_tweets with text from clean_tweets.jsonl"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import AsyncSessionLocal
from backend.models import RawTweet
from sqlalchemy import select, update

async def update_tweet_text():
    print("Reading clean tweets...")
    tweets_by_id = {}
    with open("data/clean_tweets.jsonl") as f:
        for line in f:
            data = json.loads(line)
            tweets_by_id[data['tweet_id']] = data['text']
    
    print(f"Found {len(tweets_by_id)} tweets with text")
    
    async with AsyncSessionLocal() as session:
        updated = 0
        for tweet_id, text in tweets_by_id.items():
            result = await session.execute(
                update(RawTweet)
                .where(RawTweet.tweet_id == tweet_id)
                .values(text=text)
            )
            if result.rowcount > 0:
                updated += 1
        
        await session.commit()
        print(f"✅ Updated {updated} tweets with text")

if __name__ == "__main__":
    asyncio.run(update_tweet_text())
