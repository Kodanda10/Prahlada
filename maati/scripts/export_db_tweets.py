#!/usr/bin/env python3
"""
Export raw tweets from database for Parser V2 processing
"""
import json
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncpg

# Load environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

# Convert asyncpg URL format
db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

async def export_tweets():
    """Export all raw tweets from database"""
    
    # Connect to database
    conn = await asyncpg.connect(db_url)
    
    try:
        # Simple query - just get raw tweets
        query = """
            SELECT 
                tweet_id,
                text,
                created_at,
                author_handle,
                processing_status,
                fetched_at
            FROM raw_tweets
            ORDER BY created_at DESC
        """
        
        rows = await conn.fetch(query)
        
        print(f"Found {len(rows)} tweets in database")
        
        # Export to JSONL
        output_file = Path("data/db_tweets_for_parser_v2.jsonl")
        
        with output_file.open("w", encoding="utf-8") as f:
            for row in rows:
                # Build tweet object - Parser V2 will handle raw text
                tweet = {
                    "tweet_id": row["tweet_id"],
                    "text": row["text"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "author_handle": row["author_handle"],
                    "processing_status": row["processing_status"],
                    "fetched_at": row["fetched_at"].isoformat() if row["fetched_at"] else None,
                }
                
                f.write(json.dumps(tweet, ensure_ascii=False) + "\n")
        
        print(f"✅ Exported {len(rows)} tweets to {output_file}")
        print(f"\nNote: Parser V2 will need to be updated to handle raw text input")
        print(f"      (currently expects parsed_data_v8 structure)")
        return len(rows)
        
    finally:
        await conn.close()

if __name__ == "__main__":
    count = asyncio.run(export_tweets())
    print(f"\nExported {count} tweets from database")
