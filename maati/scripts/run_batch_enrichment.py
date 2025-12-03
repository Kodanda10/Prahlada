#!/usr/bin/env python3
"""
Batch Enrichment Script: Run Gemma 3 on multiple tweets.
Supports continuous processing of all pending tweets.
"""
import asyncio
import sys
import json
import time
from pathlib import Path
from typing import List

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal
from backend.cognitive.gemma3_enrichment import Gemma3EnrichmentService
from backend.models import RawTweet, EnrichedItem
from sqlalchemy.future import select
from sqlalchemy import func

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs): return iterable

async def get_total_pending_count():
    async with AsyncSessionLocal() as session:
        # Count total raw tweets
        result = await session.execute(select(func.count(RawTweet.tweet_id)))
        total = result.scalar()
        
        # Count enriched tweets
        result = await session.execute(select(func.count(EnrichedItem.tweet_id)))
        enriched = result.scalar()
        
        return total - enriched

async def run_batch_job(batch_size: int = 10, run_all: bool = False):
    """
    Run enrichment job.
    If run_all is True, continues until no pending tweets remain.
    """
    print(f"🚀 Initializing Gemma 3 Enrichment Job...")
    
    async with AsyncSessionLocal() as session:
        service = Gemma3EnrichmentService(session)
        
        total_pending = await get_total_pending_count()
        print(f"📊 Total Pending Tweets: {total_pending}")
        
        if total_pending == 0:
            print("✅ No tweets pending enrichment.")
            return

        processed_count = 0
        
        # Determine total to process
        target_count = total_pending if run_all else min(batch_size, total_pending)
        
        print(f"🎯 Target Processing: {target_count} tweets")
        print("-" * 60)
        
        # Progress bar
        pbar = tqdm(total=target_count, unit="tweet")
        
        while processed_count < target_count:
            # Fetch next batch
            current_batch_size = min(batch_size, target_count - processed_count)
            tweets = await service.get_pending_tweets(current_batch_size)
            
            if not tweets:
                break
                
            for tweet in tweets:
                try:
                    # Enrich
                    enriched = await service.enrich_tweet(tweet)
                    
                    if enriched:
                        # Save immediately to allow resume on interrupt
                        session.add(enriched)
                        await session.commit()
                        processed_count += 1
                        pbar.update(1)
                    else:
                        print(f"\n⚠️  Enrichment returned None for {tweet.tweet_id}")
                        # Optionally mark as failed to avoid infinite loop? 
                        # For now, we rely on logs.
                        pbar.update(1) # Count as processed to move bar
                        
                except Exception as e:
                    print(f"\n❌ Error processing {tweet.tweet_id}: {e}")
                    await session.rollback()
            
            # Small pause to be nice to the system/logs
            # time.sleep(0.1) 

        pbar.close()
        print(f"\n✅ Job Complete. Processed {processed_count} tweets.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for fetching")
    parser.add_argument("--all", action="store_true", help="Process ALL pending tweets")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of tweets (overrides --all if set)")
    
    args = parser.parse_args()
    
    limit = args.limit if args.limit > 0 else args.batch_size
    run_all = args.all and args.limit == 0
    
    # If neither --all nor --limit is set, default to batch-size 10 (safe default)
    
    asyncio.run(run_batch_job(batch_size=args.batch_size, run_all=run_all))
