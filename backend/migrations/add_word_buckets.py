#!/usr/bin/env python3
"""
Migration: Add Word Buckets Tables

Creates tables for semantic word bucket extraction and clustering:
- word_buckets: Stores unique terms with embeddings
- tweet_word_buckets: Junction table linking tweets to buckets

Run: python backend/migrations/add_word_buckets.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from sqlalchemy import text
from backend.database import engine

MIGRATION_SQL = """
-- Word Buckets Table (Approved Terms)
CREATE TABLE IF NOT EXISTS word_buckets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50),
    cluster_id INTEGER,
    embedding BLOB,
    is_approved BOOLEAN DEFAULT 0,
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tweet-WordBucket Junction Table
CREATE TABLE IF NOT EXISTS tweet_word_buckets (
    tweet_id VARCHAR(255) NOT NULL,
    bucket_id INTEGER NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tweet_id, bucket_id),
    FOREIGN KEY (tweet_id) REFERENCES parsed_events(tweet_id) ON DELETE CASCADE,
    FOREIGN KEY (bucket_id) REFERENCES word_buckets(id) ON DELETE CASCADE
);

-- Indices for Performance
CREATE INDEX IF NOT EXISTS idx_word_buckets_type ON word_buckets(type);
CREATE INDEX IF NOT EXISTS idx_word_buckets_approved ON word_buckets(is_approved);
CREATE INDEX IF NOT EXISTS idx_word_buckets_cluster ON word_buckets(cluster_id);
CREATE INDEX IF NOT EXISTS idx_word_buckets_frequency ON word_buckets(frequency DESC);
CREATE INDEX IF NOT EXISTS idx_tweet_word_buckets_tweet ON tweet_word_buckets(tweet_id);
CREATE INDEX IF NOT EXISTS idx_tweet_word_buckets_bucket ON tweet_word_buckets(bucket_id);
"""

ROLLBACK_SQL = """
DROP TABLE IF EXISTS tweet_word_buckets;
DROP TABLE IF EXISTS word_buckets;
"""


async def migrate_up():
    """Apply migration"""
    print("🔄 Applying Word Buckets migration...")
    
    async with engine.begin() as conn:
        # Execute each statement separately
        for statement in MIGRATION_SQL.split(';'):
            statement = statement.strip()
            if statement:
                await conn.execute(text(statement))
    
    print("✅ Word Buckets tables created successfully")
    print("   - word_buckets (with embeddings)")
    print("   - tweet_word_buckets (junction table)")
    print("   - Indices created for performance")


async def migrate_down():
    """Rollback migration"""
    print("🔄 Rolling back Word Buckets migration...")
    
    async with engine.begin() as conn:
        for statement in ROLLBACK_SQL.split(';'):
            statement = statement.strip()
            if statement:
                await conn.execute(text(statement))
    
    print("✅ Word Buckets tables dropped")


async def main():
    """Main migration runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Word Buckets Migration")
    parser.add_argument(
        'action',
        choices=['up', 'down'],
        help='Migration action: up (apply) or down (rollback)'
    )
    
    args = parser.parse_args()
    
    if args.action == 'up':
        await migrate_up()
    else:
        await migrate_down()


if __name__ == "__main__":
    asyncio.run(main())
