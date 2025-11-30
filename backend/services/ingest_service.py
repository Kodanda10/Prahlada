"""
Ingest service for tweet ingestion operations.

Handles parsing and storing of tweet data from external sources.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging import get_logger
from ..core.exceptions import DatabaseError, ConflictError
from .. import models, schemas

logger = get_logger(__name__)


class IngestService:
    """Service for tweet ingestion operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the ingest service.
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def ingest_parsed_tweet(
        self,
        payload: schemas.IngestPayload,
    ) -> Dict[str, str]:
        """
        Ingest a parsed tweet into the database.
        
        Args:
            payload: Parsed tweet data from ingestion script
            
        Returns:
            Status response dictionary
            
        Raises:
            DatabaseError: If database operation fails
        """
        tweet_id = payload.tweet.id
        
        try:
            # Check if already exists
            existing = await self.db.get(models.ParsedEvent, tweet_id)
            if existing:
                logger.info(f"Tweet {tweet_id} already exists, skipping")
                return {
                    "status": "skipped",
                    "message": "Parsed event already exists."
                }
            
            # Create new ParsedEvent
            new_event = models.ParsedEvent(
                id=tweet_id,
                tweet_id=tweet_id,
                categories=payload.categories.model_dump(),
                gemini_metadata=payload.gemini_metadata.model_dump(),
                event_type=(
                    payload.categories.event[0]
                    if payload.categories.event else None
                ),
                locations=payload.categories.locations,
                people_mentioned=payload.categories.people,
                schemes_mentioned=payload.categories.schemes,
                overall_confidence=payload.gemini_metadata.confidence,
                parsed_at=datetime.utcnow(),
            )
            self.db.add(new_event)
            
            # Update or create raw tweet
            await self._update_or_create_raw_tweet(payload)
            
            await self.db.commit()
            
            logger.info(f"Successfully ingested tweet {tweet_id}")
            return {
                "status": "success",
                "message": f"Data for tweet {tweet_id} ingested."
            }
            
        except Exception as e:
            logger.error(f"Failed to ingest tweet {tweet_id}: {e}")
            await self.db.rollback()
            raise DatabaseError(
                message="Failed to ingest tweet data",
                operation="ingest_parsed_tweet"
            )
    
    async def _update_or_create_raw_tweet(
        self,
        payload: schemas.IngestPayload,
    ) -> None:
        """
        Update existing raw tweet or create new one.
        
        Args:
            payload: Ingestion payload with tweet data
        """
        tweet_id = payload.tweet.id
        
        raw_tweet = await self.db.get(models.RawTweet, tweet_id)
        if raw_tweet:
            raw_tweet.processing_status = 'processed'
            raw_tweet.processed_at = datetime.utcnow()
        else:
            new_raw_tweet = models.RawTweet(
                tweet_id=tweet_id,
                text=payload.tweet.text,
                created_at=payload.tweet.created_at,
                processing_status='processed',
                processed_at=datetime.utcnow(),
            )
            self.db.add(new_raw_tweet)
    
    async def check_exists(self, tweet_id: str) -> bool:
        """
        Check if a tweet has already been ingested.
        
        Args:
            tweet_id: ID to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            existing = await self.db.get(models.ParsedEvent, tweet_id)
            return existing is not None
        except Exception as e:
            logger.error(f"Failed to check tweet existence: {e}")
            raise DatabaseError(
                message="Failed to check tweet existence",
                operation="check_exists"
            )
