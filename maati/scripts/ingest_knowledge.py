import asyncio
import sys
import os
from pathlib import Path
import csv
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import engine, AsyncSessionLocal
from backend import models
from backend.knowledge_store import KnowledgeStore
from scripts.gemini_parser_v2 import GeminiParserV2
from backend.cognitive.phi_adapter import set_phi_adapter_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
    logger.info("Database tables recreated.")

async def ingest_tweets(csv_path: Path, limit: int = 10):
    """
    Ingest tweets from CSV into Knowledge Base.
    """
    # 1. Load Data
    tweets = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tweets.append(row)
            if len(tweets) >= limit:
                break
    logger.info(f"Loaded {len(tweets)} tweets from {csv_path}")

    # 2. Initialize Components
    await init_db()
    
    # Enable Phi Adapter globally
    set_phi_adapter_config(enabled=True)
    
    # Initialize Parser (Enable Cognitive Engine)
    # DEBUG: Disable semantic search to isolate hang
    parser = GeminiParserV2(enable_semantic=False)
    # Enable cognitive engine
    parser.enable_cognitive = True
    if hasattr(parser, 'phi_adapter'):
        parser.phi_adapter.enabled = True
    
    # 3. Process Loop
    async with AsyncSessionLocal() as db_session:
        knowledge_store = KnowledgeStore(db_session)
        
        for row in tweets:
            tweet_id = str(row['tweet_id'])
            text = row['raw_text']
            
            logger.info(f"Processing tweet {tweet_id}...")
            
            # Parse (Synchronous call)
            # In a real app, this might be offloaded to a worker
            row_dict = {"text": text, "tweet_id": tweet_id} # Prepare input for parser
            parsed_data = parser.parse_tweet(row_dict)
            
            # DEBUG: Print parsed location
            loc = parsed_data.get("location")
            print(f"DEBUG: Tweet {tweet_id} -> Location: {loc}", file=sys.stderr)
            sys.stderr.flush()
            
            # Save to Knowledge Base
            await knowledge_store.save_parsed_tweet(parsed_data)
        
        # Commit all changes to database
        await db_session.commit()
            
    logger.info("Ingestion complete.")

def main():
    csv_path = PROJECT_ROOT / "data" / "gold_standard_tweets.csv"
    if not csv_path.exists():
        logger.error(f"File not found: {csv_path}")
        return

    asyncio.run(ingest_tweets(csv_path, limit=10))

if __name__ == "__main__":
    main()
