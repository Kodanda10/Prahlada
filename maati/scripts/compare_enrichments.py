#!/usr/bin/env python3
"""
Comparison Script: Gemma 2 vs Gemma 3 Enrichment
Validates the parallel enrichment approach by comparing outputs side-by-side.
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal
from backend.models import RawTweet, ParsedEvent, EnrichedItem
from sqlalchemy.future import select

async def fetch_tweet_data(tweet_id: str):
    """
    Fetches the same tweet from RawTweet, ParsedEvent (Gemma 2), and EnrichedItem (Gemma 3).
    """
    async with AsyncSessionLocal() as session:
        # Get raw tweet
        result = await session.execute(select(RawTweet).where(RawTweet.tweet_id == tweet_id))
        raw = result.scalar_one_or_none()
        
        # Get ParsedEvent (Old Brain - Gemma 2)
        result = await session.execute(select(ParsedEvent).where(ParsedEvent.tweet_id == tweet_id))
        old = result.scalar_one_or_none()
        
        # Get EnrichedItem (New Brain - Gemma 3)
        result = await session.execute(select(EnrichedItem).where(EnrichedItem.tweet_id == tweet_id))
        new = result.scalar_one_or_none()
        
        return raw, old, new

def print_comparison(raw: Optional[RawTweet], old: Optional[ParsedEvent], new: Optional[EnrichedItem]):
    """
    Prints a formatted comparison of the enrichments.
    """
    print("=" * 80)
    print("ENRICHMENT COMPARISON")
    print("=" * 80)
    
    if not raw:
        print("❌ Raw tweet not found!")
        return
    
    print(f"\n📄 TWEET ID: {raw.tweet_id}")
    print(f"📅 Created: {raw.created_at}")
    print(f"👤 Author: {raw.author_handle}")
    print(f"\n📝 TEXT:\n{raw.text}")
    print("\n" + "-" * 80)
    
    # Old Brain (Gemma 2)
    print("\n🧠 OLD BRAIN (Gemma 2 - ParsedEvent)")
    print("-" * 80)
    if old:
        print(f"Event Type: {old.event_type}")
        print(f"Locations: {old.locations}")
        print(f"People: {old.people_mentioned}")
        print(f"Schemes: {old.schemes_mentioned}")
        print(f"Word Buckets: {old.word_buckets}")
        print(f"Confidence: {old.overall_confidence}")
        print(f"Review Status: {old.review_status}")
        if old.categories:
            print(f"\nCategories:")
            print(json.dumps(old.categories, indent=2, ensure_ascii=False))
    else:
        print("⚠️  Not yet processed by Gemma 2")
    
    print("\n" + "-" * 80)
    
    # New Brain (Gemma 3)
    print("\n🚀 NEW BRAIN (Gemma 3 - EnrichedItem)")
    print("-" * 80)
    if new:
        print(f"Themes (मुद्दे): {new.themes}")
        print(f"Event Type (घटना): {new.event_type}")
        print(f"Sentiment (भावना): {new.sentiment}")
        print(f"Schemes: {new.schemes}")
        print(f"Communities: {new.communities}")
        print(f"Confidence: {new.confidence_score}")
        print(f"Model: {new.model_version}")
        if new.layers:
            print(f"\n🧠 7-Layer Cognitive Model (The Boss):")
            for layer, values in new.layers.items():
                print(f"   - {layer.capitalize()}: {values}")
        
        print(f"\nPeople: {new.people}")
        print(f"Organizations: {new.organizations}")
        
        if new.location_candidates:
            print(f"\nLocation Candidates:")
            print(json.dumps(new.location_candidates, indent=2, ensure_ascii=False))
        if new.notes:
            print(f"\nNotes (विश्लेषण):\n{new.notes}")
    else:
        print("⚠️  Not yet processed by Gemma 3")
    
    print("\n" + "=" * 80)

async def compare_by_id(tweet_id: str):
    """
    Main comparison function.
    """
    raw, old, new = await fetch_tweet_data(tweet_id)
    print_comparison(raw, old, new)

async def list_available_tweets(limit: int = 10):
    """
    Lists tweets available for comparison.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(RawTweet).limit(limit))
        tweets = result.scalars().all()
        
        print(f"\n📋 Available Tweets (showing {limit}):")
        print("-" * 80)
        for tweet in tweets:
            print(f"ID: {tweet.tweet_id} | Author: {tweet.author_handle} | Date: {tweet.created_at}")
            print(f"   Text: {tweet.text[:80]}...")
            print()

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare Gemma 2 vs Gemma 3 Enrichments")
    parser.add_argument("--tweet-id", type=str, help="Specific tweet ID to compare")
    parser.add_argument("--list", action="store_true", help="List available tweets")
    parser.add_argument("--limit", type=int, default=10, help="Number of tweets to list")
    
    args = parser.parse_args()
    
    if args.list:
        await list_available_tweets(args.limit)
    elif args.tweet_id:
        await compare_by_id(args.tweet_id)
    else:
        print("Usage:")
        print("  python scripts/compare_enrichments.py --list")
        print("  python scripts/compare_enrichments.py --tweet-id <ID>")

if __name__ == "__main__":
    asyncio.run(main())
