#!/usr/bin/env python3
"""
Lite Ingestion Pipeline - No Semantic Search Dependencies

This script bypasses the heavy ML library imports (pymilvus, sentence_transformers)
while maintaining high quality through:
- Dictionary-based location resolution (GeoHierarchyResolver)
- LLM enhancement via Phi 3.5 (PhiAdapter)
- Full knowledge store integration (DB + FAISS)

Usage:
    python3 scripts/ingest_lite.py --limit 10          # Test with 10 tweets
    python3 scripts/ingest_lite.py --limit 2611        # Full ingestion
    python3 scripts/ingest_lite.py --no-llm            # Fast mode (no Phi 3.5)
"""
import asyncio
import csv
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import engine, AsyncSessionLocal
from backend import models
from backend.knowledge_store import KnowledgeStore
from backend.cognitive.phi_adapter import get_phi_adapter


# Import only the non-semantic components from gemini_parser_v2
# We'll inline the necessary parts to avoid the semantic_location_linker import

def load_json(filepath: Path) -> Dict:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


class GeoHierarchyResolverLite:
    """Lite version of GeoHierarchyResolver without semantic search."""
    
    def __init__(self):
        data_dir = PROJECT_ROOT / "data"
        
        # Load geography data
        self.constituencies = load_json(data_dir / "constituencies.json")
        self.blocks = load_json(data_dir / "blocks.json")
        self.villages = load_json(data_dir / "villages.json")
        self.ulbs = load_json(data_dir / "ulbs.json")
        
        print("✅ GeoHierarchyResolverLite initialized")
    
    def resolve_hierarchy(self, location_name: str) -> Optional[Dict]:
        """Resolve location using dictionary lookup only."""
        # Try ULB first
        if location_name in self.ulbs:
            return self.ulbs[location_name]
        
        # Try constituencies
        for district, data in self.constituencies.items():
            if location_name == district:
                return {"canonical": district, "district": district, "type": "district"}
        
        # Try blocks
        for block_name, block_data in self.blocks.items():
            if location_name == block_name:
                return {
                    "canonical": block_name,
                    "block": block_name,
                    "district": block_data.get("district"),
                    "type": "block"
                }
        
        # Try villages
        for village_name, village_data in self.villages.items():
            if location_name == village_name:
                return {
                    "canonical": village_name,
                    "village": village_name,
                    "block": village_data.get("block"),
                    "district": village_data.get("district"),
                    "type": "village"
                }
        
        return None


class LiteParser:
    """
    Lite parser with dictionary-based resolution + optional LLM enhancement.
    
    No semantic search dependencies.
    """
    
    def __init__(self, enable_llm: bool = True):
        self.enable_llm = enable_llm
        self.geo_resolver = GeoHierarchyResolverLite()
        
        if enable_llm:
            self.phi_adapter = get_phi_adapter()
            print("✅ LiteParser initialized (with Phi 3.5)")
        else:
            self.phi_adapter = None
            print("✅ LiteParser initialized (dictionary-only mode)")
    
    def parse_tweet(self, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse tweet using dictionary + optional LLM.
        
        Args:
            tweet_data: {"tweet_id": str, "text": str}
            
        Returns:
            Parsed tweet data
        """
        tweet_id = tweet_data["tweet_id"]
        text = tweet_data["text"]
        
        # Basic parsing
        parsed = {
            "tweet_id": tweet_id,
            "text": text,
            "event_type": "अन्य",  # Default
            "location": None,
            "confidence": 0.5,
            "cognitive_view": None,
            "quality_flags": {},
            "word_buckets": []
        }
        
        # Extract location using dictionary
        location_result = self._extract_location(text)
        if location_result:
            parsed["location"] = location_result
            parsed["confidence"] = 0.8
        
        # Enhance with LLM if enabled
        if self.enable_llm and self.phi_adapter:
            try:
                suggestions = self.phi_adapter.get_suggestions(
                    tweet_id=tweet_id,
                    raw_tweet=text,
                    current_parsed=parsed
                )
                
                # Apply LLM suggestions
                if suggestions.event_type_suggestions:
                    parsed["event_type"] = suggestions.event_type_suggestions[0]
                
                if suggestions.cognitive_view:
                    parsed["cognitive_view"] = suggestions.cognitive_view
                
                if suggestions.confidence_score:
                    parsed["confidence"] = suggestions.confidence_score
                
                # Store LLM metadata
                parsed["quality_flags"]["phi_enhanced"] = True
                parsed["quality_flags"]["phi_confidence"] = suggestions.confidence_score
                
            except Exception as e:
                print(f"⚠️  LLM enhancement failed for {tweet_id}: {e}")
                parsed["quality_flags"]["phi_error"] = str(e)
        
        return parsed
    
    def _extract_location(self, text: str) -> Optional[Dict]:
        """Extract location from text using dictionary matching."""
        # Simple word-based matching
        words = text.split()
        
        for word in words:
            # Try exact match
            result = self.geo_resolver.resolve_hierarchy(word)
            if result:
                return result
        
        return None


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("✅ Database initialized")


async def ingest_from_csv(
    csv_path: Path,
    limit: int = 10,
    enable_llm: bool = True
):
    """
    Ingest tweets from CSV.
    
    Args:
        csv_path: Path to CSV file
        limit: Number of tweets to process
        enable_llm: Whether to use Phi 3.5 for enhancement
    """
    # Load CSV
    tweets = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tweets.append(row)
            if len(tweets) >= limit:
                break
    
    print(f"📥 Loaded {len(tweets)} tweets from {csv_path}")
    
    # Initialize components
    await init_db()
    parser = LiteParser(enable_llm=enable_llm)
    
    # Process tweets
    async with AsyncSessionLocal() as db_session:
        knowledge_store = KnowledgeStore(db_session)
        
        processed = 0
        for row in tweets:
            tweet_id = str(row['tweet_id'])
            text = row['raw_text']
            
            print(f"\n🔄 [{processed+1}/{len(tweets)}] Processing {tweet_id}...")
            
            # Parse
            parsed_data = parser.parse_tweet({"tweet_id": tweet_id, "text": text})
            
            # Display results
            location = parsed_data.get("location")
            loc_str = location.get("canonical") if location else "None"
            print(f"   📍 Location: {loc_str}")
            print(f"   📊 Event: {parsed_data['event_type']}")
            print(f"   🎯 Confidence: {parsed_data['confidence']:.2f}")
            
            # Save to knowledge base
            await knowledge_store.save_parsed_tweet(parsed_data)
            processed += 1
        
        await db_session.commit()
    
    print(f"\n✅ Ingestion complete! Processed {processed} tweets.")
    print(f"   Mode: {'Hybrid (Dictionary + Phi 3.5)' if enable_llm else 'Fast (Dictionary only)'}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Lite Ingestion Pipeline")
    parser.add_argument("--limit", type=int, default=10, help="Number of tweets to process")
    parser.add_argument("--no-llm", action="store_true", help="Disable Phi 3.5 (fast mode)")
    parser.add_argument("--csv", type=str, default="data/gold_standard_tweets.csv", help="CSV file path")
    
    args = parser.parse_args()
    
    csv_path = PROJECT_ROOT / args.csv
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return
    
    enable_llm = not args.no_llm
    
    print(f"🚀 Starting Lite Ingestion Pipeline")
    print(f"   CSV: {csv_path}")
    print(f"   Limit: {args.limit}")
    print(f"   Mode: {'Hybrid (LLM)' if enable_llm else 'Fast (No LLM)'}")
    print()
    
    asyncio.run(ingest_from_csv(csv_path, args.limit, enable_llm))


if __name__ == "__main__":
    main()
