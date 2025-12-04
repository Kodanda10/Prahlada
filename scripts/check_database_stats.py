#!/usr/bin/env python3
"""
Quick database statistics checker for Project Prahlada.
Shows total files (tweets) and how many were enriched with Gemma 3.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

# Set up path to import models
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from backend.models import RawTweet, ParsedEvent, EnrichedItem
from backend.database import Base

def get_database_stats():
    """
    Query the database to get statistics about files/tweets and Gemma 3 enrichment.
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env file")
        return
    
    # Convert async URL to sync URL
    sync_url = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    
    # Create engine and session
    engine = create_engine(sync_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        try:
            # Get total raw tweets
            result = session.execute(select(func.count()).select_from(RawTweet))
            total_raw_tweets = result.scalar()
            
            # Get total parsed events
            result = session.execute(select(func.count()).select_from(ParsedEvent))
            total_parsed_events = result.scalar()
            
            # Get total enriched items (Gemma 3)
            result = session.execute(select(func.count()).select_from(EnrichedItem))
            total_enriched_gemma3 = result.scalar()
            
            # Get enriched items by model version
            result = session.execute(
                select(EnrichedItem.model_version, func.count())
                .group_by(EnrichedItem.model_version)
            )
            enriched_by_model = result.all()
            
            # Get processing status breakdown
            result = session.execute(
                select(RawTweet.processing_status, func.count())
                .group_by(RawTweet.processing_status)
            )
            status_breakdown = result.all()
            
            # Get review status breakdown
            result = session.execute(
                select(ParsedEvent.review_status, func.count())
                .group_by(ParsedEvent.review_status)
            )
            review_breakdown = result.all()
            
            # Print results
            print("=" * 70)
            print("📊 PROJECT PRAHLADA - DATABASE STATISTICS")
            print("=" * 70)
            print()
            
            print("🗂️  TOTAL FILES IN DATABASE:")
            print(f"   • Raw Tweets:          {total_raw_tweets:,}")
            print(f"   • Parsed Events:       {total_parsed_events:,}")
            print()
            
            print("🤖 GEMMA 3 ENRICHMENT:")
            print(f"   • Total Enriched:      {total_enriched_gemma3:,}")
            print(f"   • Percentage:          {(total_enriched_gemma3 / max(total_raw_tweets, 1) * 100):.1f}%")
            print()
            
            if enriched_by_model:
                print("📦 ENRICHMENT BY MODEL VERSION:")
                for model_version, count in enriched_by_model:
                    model_name = model_version if model_version else "Unknown"
                    print(f"   • {model_name}: {count:,}")
                print()
            
            if status_breakdown:
                print("⚙️  PROCESSING STATUS:")
                for status, count in status_breakdown:
                    print(f"   • {status}: {count:,}")
                print()
            
            if review_breakdown:
                print("✅ REVIEW STATUS:")
                for status, count in review_breakdown:
                    print(f"   • {status}: {count:,}")
                print()
            
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Error querying database: {e}")
            import traceback
            traceback.print_exc()
    
    engine.dispose()

if __name__ == "__main__":
    get_database_stats()
