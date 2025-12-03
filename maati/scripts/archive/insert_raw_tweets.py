import asyncio
import json
from datetime import datetime
import os
from backend.database import engine, AsyncSessionLocal, Base
from backend.models import RawTweet
from sqlalchemy.future import select
from sqlalchemy import text

async def insert_raw_tweets():
    # Ensure tables are created - main.py will handle this, but good to have in case.
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS raw_tweets CASCADE;"))
        await conn.run_sync(Base.metadata.create_all)

    # Path to the corrupted .jsonl file that needs to be cleaned
    input_file_path = 'clean_tweets.jsonl'
    
    # Path to the cleaned .jsonl file that you will provide (this is a placeholder)
    # For now, we will use the existing corrupted file, but this script assumes
    # a human will provide a corrected input_file_path for the actual data.
    
    raw_tweets_to_insert = []
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                tweet_data = json.loads(line)
                # Assuming the tweet_data from the file has 'tweet_id', 'text', 'created_at', 'author_handle'
                raw_tweets_to_insert.append(RawTweet(
                    tweet_id=tweet_data['tweet_id'],
                    text=tweet_data['text'],
                    created_at=datetime.fromisoformat(tweet_data['created_at'].replace('Z', '+00:00')).replace(tzinfo=None),
                    author_handle=tweet_data.get('author_handle', 'unknown')
                ))
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {input_file_path}: {e}")
        return
    except KeyError as e:
        print(f"Error: Missing key in tweet data from {input_file_path}: {e}. Ensure 'tweet_id', 'text', 'created_at' are present.")
        return

    if not raw_tweets_to_insert:
        print("No raw tweets to insert.")
        return

    async with AsyncSessionLocal() as session:
        session.add_all(raw_tweets_to_insert)
        await session.commit()
        print(f"Inserted {len(raw_tweets_to_insert)} raw tweets into the database.")

if __name__ == "__main__":
    asyncio.run(insert_raw_tweets())