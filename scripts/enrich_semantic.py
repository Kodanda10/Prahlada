#!/usr/bin/env python3
"""
Phase 2: Semantic Enrichment Post-Processing Script

Enriches all ingested tweets with Phi 3.5 reasoning for semantic understanding.

Usage:
    export PHI_ENABLED=true
    ./venv/bin/python3 scripts/enrich_semantic.py --limit 10
"""
import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent, RawTweet
from backend.cognitive.enrichment_engine import PhiEnrichmentEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/enrichment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CHECKPOINT_FILE = Path("data/enrichment_checkpoint.json")


class SemanticEnrichmentPipeline:
    def __init__(self, batch_size: int = 10, timeout: int = 60, dry_run: bool = False):
        self.batch_size = batch_size
        self.timeout = timeout
        self.dry_run = dry_run
        self.engine = PhiEnrichmentEngine(timeout=timeout)
        self.stats = {'total': 0, 'processed': 0, 'enriched': 0, 'failed': 0, 'skipped': 0, 'start_time': datetime.now()}
    
    async def load_tweets(self, session, limit=None, resume_from=None):
        query = select(ParsedEvent).order_by(ParsedEvent.parsed_at.asc())
        if resume_from:
            query = query.where(ParsedEvent.tweet_id > resume_from)
        if limit:
            query = query.limit(limit)
        result = await session.execute(query)
        tweets = result.scalars().all()
        logger.info(f"Loaded {len(tweets)} tweets for processing")
        return tweets
    
    async def enrich_batch(self, tweets, session):
        batch_stats = {'enriched': 0, 'failed': 0, 'skipped': 0}
        for tweet in tweets:
            try:
                if tweet.word_buckets and len(tweet.word_buckets) > 0:
                    logger.info(f"Skipping {tweet.tweet_id} - already enriched")
                    batch_stats['skipped'] += 1
                    continue
                
                raw_result = await session.execute(select(RawTweet).where(RawTweet.tweet_id == tweet.tweet_id))
                raw_tweet = raw_result.scalars().first()
                tweet_text = raw_tweet.text if raw_tweet else ""
                
                if not tweet_text:
                    batch_stats['skipped'] += 1
                    continue
                
                original_data = {
                    "tweet_id": tweet.tweet_id,
                    "event_type": tweet.event_type,
                    "locations": tweet.locations,
                    "people": tweet.people_mentioned,
                    "schemes": tweet.schemes_mentioned
                }
                
                logger.info(f"Enriching tweet {tweet.tweet_id}...")
                result = await self.engine.enrich_tweet(tweet.tweet_id, tweet_text, original_data)
                
                if result.success:
                    if not self.dry_run:
                        # Add semantic word buckets (our primary enrichment)
                        tweet.word_buckets = result.semantic_word_buckets or []
                        
                        # Store full Phi reasoning in cognitive_view
                        tweet.cognitive_view = result.reasoning.to_dict() if result.reasoning else {}
                        
                        # Store corrections in cognitive_view ONLY (not in main fields to avoid JSONB conflicts)
                        # The parser owns locations/event_type fields, enrichment only advises
                        if result.reasoning:
                            tweet.cognitive_view['location_corrections'] = result.location_corrections
                            tweet.cognitive_view['event_corrections'] = result.event_corrections
                        
                        # Update quality tracking
                        tweet.quality_flags = {
                            "phi_enriched": True, 
                            "enrichment_confidence": result.reasoning.confidence if result.reasoning else 0.0,
                            "has_location_suggestions": bool(result.location_corrections),
                            "has_event_suggestions": bool(result.event_corrections)
                        }
                        tweet.overall_confidence = result.reasoning.confidence if result.reasoning else tweet.overall_confidence
                        
                        # Commit all changes
                        await session.commit()
                        logger.info(f"✅ Enriched {tweet.tweet_id} - buckets: {result.semantic_word_buckets}")
                    else:
                        logger.info(f"[DRY-RUN] Would enrich {tweet.tweet_id} - buckets: {result.semantic_word_buckets}")
                    batch_stats['enriched'] += 1
                else:
                    logger.error(f"Failed to enrich {tweet.tweet_id}: {result.error_message}")
                    batch_stats['failed'] += 1
                
                self.stats['processed'] += 1
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing {tweet.tweet_id}: {e}")
                batch_stats['failed'] += 1
                await session.rollback()
        return batch_stats
    
    async def run(self, limit=None, resume=False):
        logger.info(f"🚀 Starting Phase 2: Semantic Enrichment Pipeline")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'PRODUCTION'}")
        
        resume_from = None
        if resume and CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE) as f:
                resume_from = json.load(f).get('last_tweet_id')
        
        async with AsyncSessionLocal() as session:
            tweets = await self.load_tweets(session, limit, resume_from)
            self.stats['total'] = len(tweets)
            if not tweets:
                return
            
            for i in range(0, len(tweets), self.batch_size):
                batch = tweets[i:i + self.batch_size]
                logger.info(f"\n📦 Processing batch {i//self.batch_size + 1}/{(len(tweets)+self.batch_size-1)//self.batch_size}")
                batch_stats = await self.enrich_batch(batch, session)
                self.stats['enriched'] += batch_stats['enriched']
                self.stats['failed'] += batch_stats['failed']
                self.stats['skipped'] += batch_stats['skipped']
                
                if not self.dry_run:
                    with open(CHECKPOINT_FILE, 'w') as f:
                        json.dump({'last_tweet_id': batch[-1].tweet_id, 'stats': {k: str(v) if isinstance(v, datetime) else v for k, v in self.stats.items()}}, f)
        
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        logger.info(f"\nPhase 2 Enrichment Complete!\nTotal: {self.stats['total']}\nEnriched: {self.stats['enriched']} ✅\nFailed: {self.stats['failed']} ❌\nSkipped: {self.stats['skipped']} ⏭️\nTime: {elapsed:.1f}s")


async def main():
    parser = argparse.ArgumentParser(description="Phase 2: Semantic Enrichment Pipeline")
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--timeout', type=int, default=300, help="Timeout per tweet (default: 300s = 5min, NO RESTRICTIONS for complete enrichment)")
    parser.add_argument('--limit', type=int, help="Limit number of tweets")
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    pipeline = SemanticEnrichmentPipeline(batch_size=args.batch_size, timeout=args.timeout, dry_run=args.dry_run)
    await pipeline.run(limit=args.limit, resume=args.resume)


if __name__ == "__main__":
    asyncio.run(main())
