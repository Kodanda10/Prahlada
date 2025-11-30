import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from .models import ParsedEvent, WordBucket
from .vector_store import get_vector_store
import json

logger = logging.getLogger(__name__)

class KnowledgeStore:
    """
    Handles persistence of Cognitive Knowledge into Database and Vector Store.
    """
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        # Use a dedicated index for Knowledge Base
        self.vector_store = get_vector_store(index_path="data/knowledge_base/faiss_index.bin")

    async def save_parsed_tweet(self, tweet_data: Dict[str, Any]):
        """
        Save parsed tweet data, cognitive view, and word buckets.
        """
        tweet_id = tweet_data.get("tweet_id")
        if not tweet_id:
            logger.error("Cannot save tweet without tweet_id")
            return

        # 1. Save Word Buckets
        # Extract buckets from cognitive view or semantic buckets
        buckets = tweet_data.get("word_buckets", [])
        bucket_ids = []
        
        # Also extract from cognitive view if available
        cog_view = tweet_data.get("cognitive_view", {})
        if cog_view:
            # Add sector tags as buckets
            buckets.extend(cog_view.get("sector_tags", []))
            # Add stakeholders as buckets
            stakeholders = cog_view.get("stakeholders", {})
            if isinstance(stakeholders, dict):
                for p in stakeholders.get("people", []):
                    if isinstance(p, dict): buckets.append(p.get("name"))
                for o in stakeholders.get("organizations", []):
                    if isinstance(o, dict): buckets.append(o.get("name"))

        # Deduplicate
        unique_buckets = list(set([b for b in buckets if b]))

        for term in unique_buckets:
            # Check if exists
            stmt = select(WordBucket).where(WordBucket.term == term)
            result = await self.db.execute(stmt)
            existing_bucket = result.scalar_one_or_none()

            if not existing_bucket:
                new_bucket = WordBucket(
                    term=term,
                    type="auto_extracted", # Can be refined later
                    is_approved=False
                )
                self.db.add(new_bucket)
                # We need to flush to get the ID, but we can just commit at the end
                # For now, let's just track that we processed it.
            
        # 2. Save Parsed Tweet
        # Check if exists (UPDATE) or create (INSERT)
        result = await self.db.execute(
            select(ParsedEvent).where(ParsedEvent.tweet_id == tweet_id)
        )
        existing = result.scalars().first()

        if existing:
            # Update existing record
            existing.event_type = tweet_data.get("event_type")
            existing.locations = tweet_data.get("locations", [])
            existing.people_mentioned = tweet_data.get("people", [])
            existing.schemes_mentioned = tweet_data.get("schemes", [])
            existing.word_buckets = unique_buckets
            existing.organizations = tweet_data.get("organizations", [])
            existing.gemini_metadata = tweet_data.get("gemini_metadata", {})
            existing.cognitive_view = tweet_data.get("cognitive_view") or {}
            existing.quality_flags = tweet_data.get("quality_flags") or {}
            existing.overall_confidence = tweet_data.get("confidence", 0.0)
            
        else:
            # Create new record - use tweet_id as primary key
            location_data = tweet_data.get("location")
            locations_array = [location_data.get("canonical", "")] if location_data else []
            
            event = ParsedEvent(
                id=tweet_id,  # Use tweet_id as primary key (string)
                tweet_id=tweet_id,
                event_type=tweet_data.get("event_type"),
                locations=locations_array,
                people_mentioned=tweet_data.get("entities", {}).get("people", []),
                schemes_mentioned=tweet_data.get("entities", {}).get("schemes", []),
                word_buckets=unique_buckets,
                organizations=tweet_data.get("entities", {}).get("organizations", []),
                cognitive_view=cog_view,
                quality_flags=tweet_data.get("quality_flags"),
                overall_confidence=tweet_data.get("confidence", 0.0),
                categories=tweet_data.get("categories"),
                gemini_metadata={
                    "location_full": location_data,  # Store full location data in metadata
                    "reasoning_trace": tweet_data.get("reasoning_trace"),
                    "parsing_trace": tweet_data.get("parsing_trace")
                }
            )
            self.db.add(new_event)

        try:
            await self.db.commit()
            logger.info(f"Saved knowledge for tweet {tweet_id}")
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Failed to save tweet {tweet_id}: {e}")

        # 3. Add to Vector Store
        # Combine text and reasoning for rich embedding
        raw_text = tweet_data.get("text", "")
        reasoning = tweet_data.get("reasoning_trace", "")
        combined_text = f"{raw_text} | Reasoning: {reasoning}"
        
        doc = {
            "tweet_id": tweet_id,
            "text": combined_text,
            "event_type": tweet_data.get("event_type"),
            "themes": cog_view.get("primary_theme", "") if cog_view else ""
        }
        
        # Add to vector store (this is synchronous usually, but fast enough)
        self.vector_store.add_documents([doc])
        self.vector_store.save()
