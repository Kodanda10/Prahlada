import asyncio
import json
from datetime import datetime
from backend.database import engine, AsyncSessionLocal, Base, get_db_session
from backend.models import RawTweet
from sqlalchemy import select, text

async def pull_raw_tweets():
    # Use the async session
    async with AsyncSessionLocal() as session:
        query = select(RawTweet)
        # Add a debug print to inspect the result before fetching scalars
        result = await session.execute(query)
        print(f"Query result: {result}") # Debug print
        raw_tweets = result.scalars().all()

    output_file = "raw_tweets_from_db.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for tweet in raw_tweets:
            tweet_data = {
                "tweet_id": tweet.tweet_id,
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat() + "Z", # Ensure ISO format with Z for UTC
                "author_handle": tweet.author_handle
            }
            f.write(json.dumps(tweet_data, ensure_ascii=False) + "\n")
    
    print(f"Pulled {len(raw_tweets)} raw tweets from DB and saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(pull_raw_tweets())
