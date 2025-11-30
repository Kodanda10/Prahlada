#!/usr/bin/env python3
"""
Phase 2: Semantic Enrichment Post-Processing Script

Enriches all 2,611 ingested tweets with Phi 3.5 reasoning:
- Holistic contextual understanding
- Semantic word bucket clustering
- Location/event corrections
- Vector embeddings for knowledge bank

Usage:
    # Dry run on 10 tweets
    ./venv/bin/python3 scripts/enrich_semantic.py --dry-run --limit 10
    
    # Full enrichment with resume
    ./venv/bin/python3 scripts/enrich_semantic.py --resume
    
    # Process specific batch
    ./venv/bin/python3 scripts/enrich_semantic.py --batch-size 50 --limit 100
"""
import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent
from backend.cognitive.enrichment_engine import PhiEnrichmentEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/enrichment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Checkpoint file
CHECKPOINT_FILE = Path("data/enrichment_checkpoint.json")


class SemanticEnrichmentPipeline:
    """
    Post-processing pipeline for semantic enrichment.
    
    Processes tweets in batches, generating Phi reasoning and
    enriching semantic fields in the database.
    """
    
    def __init__(
        self,
        batch_size: int = 10,
        timeout: int = 60,
        dry_run: bool = False
    ):
        """
        Initialize enrichment pipeline.
        
        Args:
            batch_size: Number of tweets per batch
            timeout: Timeout per tweet in seconds
            dry_run: If True, don't update database
        """
        self.batch_size = batch_size
        self.timeout = timeout
        self.dry_run = dry_run
        self.engine = PhiEnrichmentEngine(timeout=timeout)
        
        self.stats = {
            'total': 0,
            'processed': 0,
            'enriched': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now()
        }
    
    async def load_tweets(
        self,
        session: AsyncSession,
        limit: int = None,
        resume_from: str = None
    ) -> List[ParsedEvent]:
        """
        Load tweets to process from database.
        
        Args:
            session: Database session
            limit: Max number of tweets to load
            resume_from: Tweet ID to resume from
            
        Returns:
            List of ParsedEvent objects
        """
        query = select(ParsedEvent).order_by(ParsedEvent.parsed_at.asc())
        
        # Resume from checkpoint
        if resume_from:
            query = query.where(ParsedEvent.tweet_id > resume_from)
        
        if limit:
            query = query.limit(limit)
        
        result = await session.execute(query)
        tweets = result.scalars().all()
        
        logger.info(f"Loaded {len(tweets)} tweets for processing")
        return tweets
    
    async def enrich_batch(
        self,
        tweets: List[ParsedEvent],
        session: AsyncSession
    ) -> Dict[str, int]:
        """
        Enrich a batch of tweets.
        
        Args:
            tweets: List of ParsedEvent objects
            session: Database session
            
        Returns:
            Stats dictionary
        """
        batch_stats = {'enriched': 0, 'failed': 0, 'skipped': 0}
        
        for tweet in tweets:
            try:
                # Skip if already enriched (has semantic_word_buckets)
                if tweet.word_buckets and len(tweet.word_buckets) > 0:
                    logger.info(f"Skipping {tweet.tweet_id} - already has word buckets")
                    batch_stats['skipped'] += 1
                    continue
                
                # Get raw text from associated RawTweet (if available)
                # For now, use a placeholder - in production, join with raw_tweets
                from sqlalchemy import select as sql_select
                from backend.models import RawTweet
                
                raw_result = await session.execute(
                    sql_select(RawTweet).where(RawTweet.tweet_id == tweet.tweet_id)
                )
                raw_tweet = raw_result.scalars().first()
                tweet_text = raw_tweet.text if raw_tweet else ""
                
                if not tweet_text:
                    logger.warning(f"No text for {tweet.tweet_id}, skipping")
                    batch_stats['skipped'] += 1
                    continue
                
                # Prepare original data
                original_data = {
                    "tweet_id": tweet.tweet_id,
                    "event_type": tweet.event_type,
                    "locations": tweet.locations,
                    "people": tweet.people_mentioned,
                    "schemes": tweet.schemes_mentioned
                }
                
                logger.info(f"Enriching tweet {tweet.tweet_id}...")
                
                # Enrich tweet
                result = await self.engine.enrich_tweet(
                    tweet_id=tweet.tweet_id,
                    tweet_text=tweet_text,
                    original_data=original_data
                )
                
                if result.success:
                    # Update database (unless dry-run)
                    if not self.dry_run:
                        tweet.word_buckets = result.semantic_word_buckets or []
                        tweet.cognitive_view = result.reasoning.to_dict() if result.reasoning else {}
                        tweet.quality_flags = {
                            "phi_enriched": True,
                            "enrichment_confidence": result.reasoning.confidence if result.reasoning else 0.0
                        }
                        tweet.overall_confidence = result.reasoning.confidence if result.reasoning else tweet.overall_confidence
                        
                        await session.commit()
                        logger.info(f"✅ Enriched {tweet.tweet_id} - buckets: {result.semantic_word_buckets}")
                    else:
                        logger.info(f"[DRY-RUN] Would enrich {tweet.tweet_id} - buckets: {result.semantic_word_buckets}")
                    
                    batch_stats['enriched'] += 1
                else:
                    logger.error(f"Failed to enrich {tweet.tweet_id}: {result.error_message}")
                    batch_stats['failed'] += 1
                
                self.stats['processed'] += 1
                
                # Small delay to avoid overwhelming Ollama
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing {tweet.tweet_id}: {e}")
                batch_stats['failed'] += 1
                await session.rollback()
        
        return batch_stats
    
    async def run(
        self,
        limit: int = None,
        resume: bool = False
    ):
        """
        Run the enrichment pipeline.
        
        Args:
            limit: Max number of tweets to process
            resume: Resume from checkpoint
        """
        logger.info("🚀 Starting Phase 2: Semantic Enrichment Pipeline")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'PRODUCTION'}")
        logger.info(f"Batch size: {self.batch_size}, Timeout: {self.timeout}s")
        
        # Load checkpoint if resuming
        resume_from = None
        if resume and CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE) as f:
                checkpoint = json.load(f)
                resume_from = checkpoint.get('last_tweet_id')
                logger.info(f"Resuming from tweet {resume_from}")
        
        async with AsyncSessionLocal() as session:
            # Load tweets
            tweets = await self.load_tweets(session, limit, resume_from)
            self.stats['total'] = len(tweets)
            
            if not tweets:
                logger.info("No tweets to process")
                return
            
            # Process in batches
            for i in range(0, len(tweets), self.batch_size):
                batch = tweets[i:i + self.batch_size]
                batch_num = i // self.batch_size + 1
                total_batches = (len(tweets) + self.batch_size - 1) // self.batch_size
                
                logger.info(f"\n📦 Processing batch {batch_num}/{total_batches}")
                
                batch_stats = await self.enrich_batch(batch, session)
                
                self.stats['enriched'] += batch_stats['enriched']
                self.stats['failed'] += batch_stats['failed']
                self.stats['skipped'] += batch_stats['skipped']
                
                # Save checkpoint
                if not self.dry_run:
                    self._save_checkpoint(batch[-1].tweet_id)
                
                # Progress report
                self._print_progress()
        
        # Final report
        self._print_final_report()
    
    def _save_checkpoint(self, last_tweet_id: str):
        """Save checkpoint for resume capability."""
        checkpoint = {
            'last_tweet_id': last_tweet_id,
            'stats': self.stats.copy(),
            'timestamp': datetime.now().isoformat()
        }
        checkpoint['stats']['start_time'] = checkpoint['stats']['start_time'].isoformat()
        
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def _print_progress(self):
        """Print progress statistics."""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        rate = self.stats['processed'] / elapsed if elapsed > 0 else 0
        
        logger.info(f"""
Progress:
  Processed: {self.stats['processed']}/{self.stats['total']} ({self.stats['processed']*100//self.stats['total'] if self.stats['total'] > 0 else 0}%)
  Enriched: {self.stats['enriched']}
  Failed: {self.stats['failed']}
  Skipped: {self.stats['skipped']}
  Rate: {rate:.2f} tweets/sec
  Elapsed: {elapsed:.1f}s
""")
    
    def _print_final_report(self):
        """Print final enrichment report."""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        logger.info(f"""
{'='*60}
Phase 2 Enrichment Complete!
{'='*60}
Total Tweets: {self.stats['total']}
Enriched: {self.stats['enriched']} ✅
Failed: {self.stats['failed']} ❌
Skipped: {self.stats['skipped']} ⏭️
Total Time: {elapsed:.1f}s
Average: {elapsed/self.stats['processed'] if self.stats['processed'] > 0 else 0:.2f}s/tweet
{'='*60}
""")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Phase 2: Semantic Enrichment Pipeline")
    parser.add_argument('--batch-size', type=int, default=10, help="Batch size (default: 10)")
    parser.add_argument('--timeout', type=int, default=60, help="Timeout per tweet in seconds (default: 60)")
    parser.add_argument('--limit', type=int, help="Limit number of tweets to process")
    parser.add_argument('--resume', action='store_true', help="Resume from checkpoint")
    parser.add_argument('--dry-run', action='store_true', help="Dry run (don't update database)")
    
    args = parser.parse_args()
    
    pipeline = SemanticEnrichmentPipeline(
        batch_size=args.batch_size,
        timeout=args.timeout,
        dry_run=args.dry_run
    )
    
    await pipeline.run(limit=args.limit, resume=args.resume)


if __name__ == "__main__":
    asyncio.run(main())
