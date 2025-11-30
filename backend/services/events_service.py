"""
Events service for parsed event operations.

Handles CRUD operations for parsed events and their metadata.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.logging import get_logger
from ..core.exceptions import DatabaseError, NotFoundError
from .. import models

logger = get_logger(__name__)


class EventsService:
    """Service for managing parsed events."""
    
    # Status mapping from raw statuses to display statuses
    STATUS_MAP = {
        "failed": "failed",
        "error": "failed",
        "pending": "pending",
        "pending_retry": "pending_retry",
        "success": "processed",
        "processed": "processed",
        "completed": "processed",
    }
    
    # Display status mapping for responses
    DISPLAY_STATUS_MAP = {
        "processed": "SUCCESS",
        "pending": "PENDING",
        "pending_retry": "PENDING",
        "failed": "FAILED",
    }
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the events service.
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def get_events(
        self,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get parsed events with optional status filtering.
        
        Args:
            status: Optional status filter (success, failed, pending)
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            # Normalize and map status filter
            status_filter = None
            if status:
                normalized = status.lower()
                status_filter = self.STATUS_MAP.get(normalized)
            
            # Build query
            query = (
                select(models.ParsedEvent, models.RawTweet)
                .join(
                    models.RawTweet,
                    models.RawTweet.tweet_id == models.ParsedEvent.tweet_id,
                    isouter=True
                )
                .order_by(models.ParsedEvent.parsed_at.desc())
                .limit(limit)
            )
            
            if status_filter:
                query = query.where(
                    models.RawTweet.processing_status == status_filter
                )
            
            # Execute query
            results = await self.db.execute(query)
            rows = results.all()
            
            # Transform results
            events = []
            for parsed_event, raw_tweet in rows:
                events.append(self._transform_event(parsed_event, raw_tweet))
            
            logger.info(f"Retrieved {len(events)} events (filter: {status})")
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            raise DatabaseError(
                message="Failed to retrieve events",
                operation="get_events"
            )
    
    async def get_event_by_id(self, tweet_id: str) -> Optional[models.ParsedEvent]:
        """
        Get a single event by tweet ID.
        
        Args:
            tweet_id: Tweet ID to look up
            
        Returns:
            ParsedEvent if found, None otherwise
        """
        try:
            event = await self.db.get(models.ParsedEvent, tweet_id)
            return event
        except Exception as e:
            logger.error(f"Failed to get event {tweet_id}: {e}")
            raise DatabaseError(
                message="Failed to retrieve event",
                operation="get_event_by_id"
            )
    
    async def approve_event(
        self,
        tweet_id: str,
        reviewer: str,
    ) -> Dict[str, str]:
        """
        Approve a parsed event.
        
        Args:
            tweet_id: ID of the event to approve
            reviewer: Username of the reviewer
            
        Returns:
            Success response dictionary
            
        Raises:
            NotFoundError: If event doesn't exist
            DatabaseError: If update fails
        """
        try:
            event = await self.db.get(models.ParsedEvent, tweet_id)
            if not event:
                raise NotFoundError(
                    resource="Event",
                    identifier=tweet_id
                )
            
            event.review_status = "approved"
            event.needs_review = False
            event.reviewed_at = datetime.utcnow()
            event.reviewed_by = reviewer
            
            await self.db.commit()
            
            logger.info(f"Event {tweet_id} approved by {reviewer}")
            return {
                "status": "success",
                "message": f"Event {tweet_id} approved"
            }
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to approve event {tweet_id}: {e}")
            raise DatabaseError(
                message="Failed to approve event",
                operation="approve_event"
            )
    
    def _transform_event(
        self,
        parsed_event: models.ParsedEvent,
        raw_tweet: Optional[models.RawTweet],
    ) -> Dict[str, Any]:
        """
        Transform database models to response format.
        
        Args:
            parsed_event: ParsedEvent model
            raw_tweet: Optional RawTweet model
            
        Returns:
            Dictionary in API response format
        """
        categories = parsed_event.categories or {}
        
        # Extract event types
        event_types = self._as_list(
            categories.get("event") or parsed_event.event_type
        )
        
        # Extract scheme tags
        scheme_tags = self._as_list(
            categories.get("schemes") or parsed_event.schemes_mentioned
        )
        
        # Get text content
        raw_text = ""
        if raw_tweet and raw_tweet.text:
            raw_text = raw_tweet.text
        elif categories.get("raw_text"):
            raw_text = categories.get("raw_text")
        elif categories.get("clean_text"):
            raw_text = categories.get("clean_text")
        
        clean_text = (
            categories.get("clean_text")
            or categories.get("summary")
            or raw_text
        )
        
        # Resolve locations
        location_text = self._resolve_locations(
            categories,
            parsed_event.locations
        )
        
        # Build log entries
        log_entries = [f"parsed_at={parsed_event.parsed_at.isoformat()}"]
        if raw_tweet and raw_tweet.processing_status:
            log_entries.append(
                f"processing_status={raw_tweet.processing_status}"
            )
        
        # Map status
        raw_status = raw_tweet.processing_status if raw_tweet else None
        display_status = self._map_status(raw_status)
        
        return {
            "tweet_id": parsed_event.tweet_id,
            "created_at": (
                raw_tweet.created_at if raw_tweet and raw_tweet.created_at
                else parsed_event.parsed_at
            ),
            "raw_text": raw_text,
            "clean_text": clean_text,
            "event_type": event_types,
            "location_text": location_text,
            "scheme_tags": scheme_tags,
            "parsing_status": display_status,
            "logs": log_entries or ["Loaded from parsed_events"],
        }
    
    def _as_list(self, value: Any) -> List[str]:
        """Convert value to a list of strings."""
        if not value:
            return []
        if isinstance(value, list):
            return [item for item in value if item]
        return [value]
    
    def _resolve_locations(
        self,
        categories: Dict[str, Any],
        stored_locations: Optional[List[str]],
    ) -> str:
        """Resolve location text from categories and stored locations."""
        names: List[str] = []
        
        cat_locations = categories.get("locations") if categories else None
        if isinstance(cat_locations, list):
            for loc in cat_locations:
                if isinstance(loc, str):
                    names.append(loc)
                elif isinstance(loc, dict):
                    label = (
                        loc.get("name")
                        or loc.get("text")
                        or loc.get("value")
                    )
                    if label:
                        names.append(label)
        
        if stored_locations:
            names.extend([loc for loc in stored_locations if loc])
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for name in names:
            if name not in seen:
                seen.add(name)
                unique.append(name)
        
        return ", ".join(unique) if unique else "Unknown"
    
    def _map_status(self, raw_status: Optional[str]) -> str:
        """Map raw status to display status."""
        if not raw_status:
            return "SUCCESS"
        return self.DISPLAY_STATUS_MAP.get(
            raw_status.lower(),
            "SUCCESS"
        )
