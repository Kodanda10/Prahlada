#!/usr/bin/env python3
"""
Dashboard Ingestion Monitor

Real-time monitor for enriched tweets showing live stats for dashboard deployment.
Watches parsed_events table and displays enrichment progress.
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent


async def get_enrichment_stats():
    """Get current enrichment statistics."""
    async with AsyncSessionLocal() as session:
        # Total tweets
        total_result = await session.execute(
            select(func.count()).select_from(ParsedEvent)
        )
        total = total_result.scalar()
        
        # Enriched tweets (non-null word_buckets)
        enriched_result = await session.execute(
            select(func.count()).select_from(ParsedEvent)
            .where(ParsedEvent.word_buckets.isnot(None))
        )
        enriched = enriched_result.scalar()
        
        # Enriched with populated buckets (not empty array)
        populated_result = await session.execute(
            select(func.count()).select_from(ParsedEvent)
            .where(ParsedEvent.word_buckets.isnot(None))
            .where(func.array_length(ParsedEvent.word_buckets, 1).isnot(None))
        )
        populated = populated_result.scalar()
        
        # Latest enriched tweets
        latest_result = await session.execute(
            select(ParsedEvent)
            .where(ParsedEvent.word_buckets.isnot(None))
            .order_by(ParsedEvent.parsed_at.desc())
            .limit(5)
        )
        latest = latest_result.scalars().all()
        
        return {
            'total': total,
            'enriched': enriched,
            'populated': populated,
            'latest': latest
        }


async def monitor_loop(interval_seconds=5):
    """Continuously monitor enrichment progress."""
    print("🔄 Dashboard Ingestion Monitor Started")
    print("=" * 60)
    print()
    
    previous_enriched = 0
    
    while True:
        try:
            stats = await get_enrichment_stats()
            
            # Clear screen (optional)
            # print("\033[2J\033[H", end="")
            
            # Header
            print(f"📊 Dashboard Ingestion Monitor - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            print()
            
            # Overall stats
            total = stats['total']
            enriched = stats['enriched']
            populated = stats['populated']
            
            enriched_pct = (enriched / total * 100) if total > 0 else 0
            populated_pct = (populated / enriched * 100) if enriched > 0 else 0
            
            print(f"📈 Overall Progress:")
            print(f"   Total tweets:      {total:,}")
            print(f"   Enriched:          {enriched:,} ({enriched_pct:.1f}%)")
            print(f"   With word buckets: {populated:,} ({populated_pct:.1f}%)")
            print(f"   Empty buckets:     {enriched - populated:,}")
            print()
            
            # Rate calculation
            new_enriched = enriched - previous_enriched
            if new_enriched > 0:
                rate_per_min = (new_enriched / interval_seconds) * 60
                print(f"⚡ Current Rate: +{new_enriched} in {interval_seconds}s (~{rate_per_min:.1f}/min)")
                print()
            previous_enriched = enriched
            
            # Dashboard readiness
            print(f"🎯 Dashboard Status:")
            home_ready = enriched
            review_ready = enriched
            analytics_ready = populated  # Only populated buckets for analytics
            
            print(f"   Home page ready:      {home_ready:,} tweets")
            print(f"   Review page ready:    {review_ready:,} tweets")
            print(f"   Analytics ready:      {analytics_ready:,} tweets (HOLD)")
            print()
            
            # Latest enriched
            print(f"📝 Latest 5 Enriched:")
            for tweet in stats['latest'][:5]:
                buckets = tweet.word_buckets or []
                bucket_str = ", ".join(buckets[:3]) if buckets else "[]"
                if len(buckets) > 3:
                    bucket_str += f" +{len(buckets)-3} more"
                
                print(f"   {tweet.tweet_id[:10]}... | {tweet.event_type[:15]:15} | [{bucket_str}]")
            
            print()
            print("=" * 60)
            print(f"Next update in {interval_seconds}s... (Ctrl+C to stop)")
            print()
            
            await asyncio.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            print("\n\n✅ Monitor stopped")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await asyncio.sleep(interval_seconds)


async def show_sample_enriched(count=10):
    """Show sample enriched tweets for verification."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ParsedEvent)
            .where(ParsedEvent.word_buckets.isnot(None))
            .where(func.array_length(ParsedEvent.word_buckets, 1).isnot(None))
            .order_by(ParsedEvent.parsed_at.desc())
            .limit(count)
        )
        tweets = result.scalars().all()
        
        print(f"\n🔍 Sample {count} Enriched Tweets:")
        print("=" * 80)
        
        for i, tweet in enumerate(tweets, 1):
            print(f"\n{i}. Tweet ID: {tweet.tweet_id}")
            print(f"   Event: {tweet.event_type}")
            print(f"   Locations: {tweet.locations}")
            print(f"   Word Buckets: {tweet.word_buckets}")
            print(f"   Confidence: {tweet.overall_confidence:.2f}")
            
            # Check if quality_flags exists and is not None
            if hasattr(tweet, 'quality_flags') and tweet.quality_flags:
                enriched = tweet.quality_flags.get('phi_enriched', False)
                conf = tweet.quality_flags.get('enrichment_confidence', 0)
                print(f"   Phi Enriched: {enriched} (conf: {conf:.2f})")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor dashboard ingestion")
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring mode')
    parser.add_argument('--sample', type=int, default=10, help='Show N sample tweets')
    parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
    
    args = parser.parse_args()
    
    if args.watch:
        asyncio.run(monitor_loop(args.interval))
    else:
        asyncio.run(show_sample_enriched(args.sample))
