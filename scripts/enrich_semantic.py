#!/usr/bin/env python3
"""
IMPORTANT: Ensure the database has a `word_buckets` text[] column on `parsed_events`
before running this script; missing the column causes an asyncpg UndefinedColumnError
and the enrichment runner stops immediately. Fix by applying the column (e.g.,
`ALTER TABLE parsed_events ADD COLUMN word_buckets text[];`) or running the matching
migration, then re-run with --resume.

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
import os
import time
sys.path.insert(0, str(Path(__file__).parent.parent))

# Force logs to IST
os.environ["TZ"] = "Asia/Kolkata"
try:
    time.tzset()
except AttributeError:
    pass  # tzset not available on all platforms

from sqlalchemy import select
from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent, RawTweet
from backend.cognitive.enrichment_engine import PhiEnrichmentEngine
import inspect
print(f"DEBUG: PhiEnrichmentEngine loaded from: {inspect.getfile(PhiEnrichmentEngine)}")
print(f"DEBUG: Has _build_reasoning_prompt? {hasattr(PhiEnrichmentEngine, '_build_reasoning_prompt')}")

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
    def __init__(self, batch_size: int = 10, timeout: int = 60, dry_run: bool = False, force: bool = False):
        self.batch_size = batch_size
        self.timeout = timeout
        self.dry_run = dry_run
        self.force = force
        self.engine = PhiEnrichmentEngine(timeout=timeout)
        self.stats = {'total': 0, 'processed': 0, 'enriched': 0, 'failed': 0, 'skipped': 0, 'start_time': datetime.now()}
    
    async def load_tweets(self, session, limit=None, resume_from=None, id_filter=None):
        query = select(ParsedEvent).order_by(ParsedEvent.parsed_at.asc())
        if resume_from:
            query = query.where(ParsedEvent.tweet_id > resume_from)
        if id_filter:
            query = query.where(ParsedEvent.tweet_id.in_(id_filter))
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
                if not self.force and tweet.word_buckets and len(tweet.word_buckets) > 0:
                    logger.info(f"Skipping {tweet.tweet_id} - already enriched")
                    batch_stats['skipped'] += 1
                    continue
                
                raw_result = await session.execute(select(RawTweet).where(RawTweet.tweet_id == tweet.tweet_id))
                raw_tweet = raw_result.scalars().first()
                tweet_text = raw_tweet.text if raw_tweet else ""
                
                if not tweet_text:
                    batch_stats['skipped'] += 1
                    continue
                
                categories = tweet.categories or {}
                metadata = tweet.gemini_metadata or {}
                loc_detail = {}
                if isinstance(categories, dict):
                    loc_detail = categories.get("location") or {}
                    # Some parsers store hierarchy separately
                    if not loc_detail:
                        loc_detail = categories.get("geo_hierarchy") or {}
                original_data = {
                    "tweet_id": tweet.tweet_id,
                    "event_type": tweet.event_type,
                    "locations": tweet.locations,
                    "people": tweet.people_mentioned,
                    "schemes": tweet.schemes_mentioned or categories.get("schemes") if isinstance(categories, dict) else [],
                    "organizations": categories.get("organizations") if isinstance(categories, dict) else [],
                    "communities": categories.get("communities") if isinstance(categories, dict) else [],
                    "location_detail": loc_detail,
                    "hierarchy_path": loc_detail.get("hierarchy_path") if isinstance(loc_detail, dict) else [],
                    "categories": categories,
                    "metadata": metadata
                }

                if loc_detail:
                    logger.info(
                        f"[LOC] {tweet.tweet_id} hierarchy={loc_detail.get('hierarchy_path')} "
                        f"district={loc_detail.get('district')} ulb={loc_detail.get('ulb')} village={loc_detail.get('village')}"
                    )
                
                logger.info(f"Enriching tweet {tweet.tweet_id}...")
                try:
                    result = await self.engine.enrich_tweet(tweet.tweet_id, tweet_text, original_data)
                except Exception as e:
                    logger.error(f"Failed to enrich {tweet.tweet_id}: {str(e)}")
                    batch_stats['failed'] += 1
                    continue
                
                if result.success:
                    if not self.dry_run:
                        # Add semantic word buckets (PRIMARY enrichment goal)
                        tweet.word_buckets = result.semantic_word_buckets or []
                        
                        # Store full Phi reasoning in cognitive_view for transparency
                        tweet.cognitive_view = result.reasoning.to_dict() if result.reasoning else {}
                        
                        # Apply Phi corrections to improve parser output
                        # (locations is ARRAY type, event_type is VARCHAR - both compatible)
                        
                        # Apply location corrections (high confidence >75%)
                        if result.location_corrections:
                            corrected_locations = []
                            for loc, correction in result.location_corrections.items():
                                # Convert confidence to float (Phi may return string)
                                conf = float(correction.get('confidence', 0))
                                if conf > 0.75:
                                    corrected_locations.append(loc)
                            if corrected_locations:
                                tweet.locations = corrected_locations  # Direct assignment (list format)
                                logger.info(f"  📍 Location corrected: {corrected_locations}")
                        
                        # Apply event type corrections (high confidence >70%)
                        if result.event_corrections:
                            # Convert confidence to float (Phi may return string)
                            conf = float(result.event_corrections.get('confidence', 0))
                            if conf > 0.7:
                                tweet.event_type = result.event_corrections['nuance']  # Direct assignment (str)
                                logger.info(f"  🎯 Event corrected: {tweet.event_type}")
                        
                        # Update quality tracking
                        tweet.quality_flags = {
                            "phi_enriched": True, 
                            "enrichment_confidence": result.reasoning.confidence if result.reasoning else 0.0,
                            "locations_corrected": bool(result.location_corrections),
                            "event_corrected": bool(result.event_corrections)
                        }
                        tweet.overall_confidence = result.reasoning.confidence if result.reasoning else tweet.overall_confidence
                        
                        # Commit all changes atomically
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
    
    async def run(self, limit=None, resume=False, id_filter=None):
        logger.info(f"🚀 Starting Phase 2: Semantic Enrichment Pipeline")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'PRODUCTION'}")
        
        resume_from = None
        if resume and CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE) as f:
                resume_from = json.load(f).get('last_tweet_id')
        
        async with AsyncSessionLocal() as session:
            tweets = await self.load_tweets(session, limit, resume_from, id_filter)
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
    parser.add_argument('--force', action='store_true', help="Force re-enrichment of all tweets, even if already enriched")
    parser.add_argument('--id-file', type=str, help="Path to file containing tweet IDs (one per line) to process")
    args = parser.parse_args()

    id_filter = None
    if args.id_file:
        from pathlib import Path
        id_path = Path(args.id_file)
        if not id_path.exists():
            logger.error(f"ID file not found: {id_path}")
            sys.exit(1)
        with open(id_path) as f:
            id_filter = [line.strip() for line in f if line.strip()]
    
    pipeline = SemanticEnrichmentPipeline(batch_size=args.batch_size, timeout=args.timeout, dry_run=args.dry_run, force=args.force)
    await pipeline.run(limit=args.limit, resume=args.resume, id_filter=id_filter)


if __name__ == "__main__":
    asyncio.run(main())
