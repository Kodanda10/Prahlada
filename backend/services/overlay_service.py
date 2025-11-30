"""
Overlay service for human-reviewed corrections.

Provides a safe layer for applying approved human corrections to parsed data
without modifying the original parser outputs.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from ..core.logging import get_logger
from ..core.config import settings

logger = get_logger(__name__)


class OverlayRecord:
    """Human-reviewed correction record."""

    def __init__(
        self,
        tweet_id: str,
        field: str,
        corrected_value: Any,
        reviewer_id: str = "SYSTEM",
        reviewer_name: Optional[str] = None,
        source: str = "human_review",
        confidence: float = 1.0,
        notes: Optional[str] = None
    ):
        self.tweet_id = tweet_id
        self.field = field
        self.corrected_value = corrected_value
        self.reviewer_id = reviewer_id
        self.reviewer_name = reviewer_name
        self.source = source
        self.confidence = confidence
        self.notes = notes
        self.created_at = datetime.utcnow().isoformat()
        self.id = f"overlay_{tweet_id}_{field}_{int(datetime.utcnow().timestamp())}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "tweet_id": self.tweet_id,
            "field": self.field,
            "corrected_value": self.corrected_value,
            "reviewer_id": self.reviewer_id,
            "reviewer_name": self.reviewer_name,
            "source": self.source,
            "confidence": self.confidence,
            "notes": self.notes,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OverlayRecord':
        """Create from dictionary."""
        record = cls(
            tweet_id=data["tweet_id"],
            field=data["field"],
            corrected_value=data["corrected_value"],
            reviewer_id=data.get("reviewer_id", "SYSTEM"),
            reviewer_name=data.get("reviewer_name"),
            source=data.get("source", "human_review"),
            confidence=data.get("confidence", 1.0),
            notes=data.get("notes")
        )
        record.id = data.get("id", record.id)
        record.created_at = data.get("created_at", record.created_at)
        return record


class OverlayService:
    """
    Service for managing human-reviewed corrections.

    Provides safe overlay functionality without modifying core parser data.
    """

    def __init__(self, overlay_dir: Optional[str] = None):
        """
        Initialize overlay service.

        Args:
            overlay_dir: Directory for overlay storage (defaults to config setting)
        """
        self.overlay_dir = Path(overlay_dir or settings.LEARNED_RULES_DIR)
        self.overlay_dir.mkdir(parents=True, exist_ok=True)
        self._overlays: Dict[str, List[OverlayRecord]] = {}
        self._loaded = False

    def _ensure_loaded(self):
        """Lazy load overlays from disk."""
        if not self._loaded:
            self._load_overlays()
            self._loaded = True

    def _load_overlays(self):
        """Load overlay records from disk."""
        overlay_file = self.overlay_dir / "overlays.json"

        if overlay_file.exists():
            try:
                with open(overlay_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for record_data in data.get("overlays", []):
                    record = OverlayRecord.from_dict(record_data)
                    if record.tweet_id not in self._overlays:
                        self._overlays[record.tweet_id] = []
                    self._overlays[record.tweet_id].append(record)

                logger.info(f"Loaded {len(self._overlays)} overlay records")
            except Exception as e:
                logger.warning(f"Failed to load overlays: {e}")
                self._overlays = {}

    def _save_overlays(self):
        """Save overlay records to disk."""
        overlay_file = self.overlay_dir / "overlays.json"

        try:
            data = {
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0",
                    "total_overlays": sum(len(records) for records in self._overlays.values())
                },
                "overlays": [
                    record.to_dict()
                    for records in self._overlays.values()
                    for record in records
                ]
            }

            with open(overlay_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Saved {data['metadata']['total_overlays']} overlay records")
        except Exception as e:
            logger.error(f"Failed to save overlays: {e}")

    def add_overlay(
        self,
        tweet_id: str,
        field: str,
        corrected_value: Any,
        reviewer_id: str = "SYSTEM",
        reviewer_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> OverlayRecord:
        """
        Add a human-reviewed correction overlay.

        Args:
            tweet_id: Tweet identifier
            field: Field that was corrected (e.g., "event_type", "locations")
            corrected_value: The approved corrected value
            reviewer_id: ID of the reviewer
            reviewer_name: Name of the reviewer
            notes: Optional notes about the correction

        Returns:
            The created overlay record
        """
        self._ensure_loaded()

        record = OverlayRecord(
            tweet_id=tweet_id,
            field=field,
            corrected_value=corrected_value,
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            notes=notes
        )

        if tweet_id not in self._overlays:
            self._overlays[tweet_id] = []
        self._overlays[tweet_id].append(record)

        self._save_overlays()

        logger.info(f"Added overlay for tweet {tweet_id}, field {field}", extra={
            "reviewer_id": reviewer_id,
            "overlay_id": record.id
        })

        return record

    def get_overlays_for_tweet(self, tweet_id: str) -> List[OverlayRecord]:
        """
        Get all approved overlays for a specific tweet.

        Args:
            tweet_id: Tweet identifier

        Returns:
            List of overlay records for the tweet
        """
        self._ensure_loaded()
        return self._overlays.get(tweet_id, [])

    def apply_overlays(self, parsed_data: Dict[str, Any], tweet_id: str) -> Dict[str, Any]:
        """
        Apply approved overlays to parsed data.

        This creates a modified copy without affecting the original data.

        Args:
            parsed_data: Original parsed data from core parser
            tweet_id: Tweet identifier

        Returns:
            Parsed data with overlays applied where available
        """
        self._ensure_loaded()

        # Create a deep copy to avoid modifying original
        result = json.loads(json.dumps(parsed_data))

        overlays = self.get_overlays_for_tweet(tweet_id)
        if not overlays:
            return result

        # Apply overlays (most recent first, but we'll use approved ones)
        applied_fields = set()

        for overlay in overlays:
            if overlay.field not in applied_fields:
                # Only apply if we have high confidence or it's from human review
                if overlay.confidence >= 0.8 or overlay.source == "human_review":
                    result[overlay.field] = overlay.corrected_value
                    applied_fields.add(overlay.field)
                    logger.debug(f"Applied overlay for field {overlay.field}", extra={
                        "tweet_id": tweet_id,
                        "overlay_id": overlay.id
                    })

        if applied_fields:
            logger.info(f"Applied {len(applied_fields)} overlays to tweet {tweet_id}")

        return result

    def get_overlay_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored overlays.

        Returns:
            Dictionary with overlay statistics
        """
        self._ensure_loaded()

        total_overlays = sum(len(records) for records in self._overlays.values())
        tweets_with_overlays = len(self._overlays)

        field_counts = {}
        reviewer_counts = {}

        for records in self._overlays.values():
            for record in records:
                field_counts[record.field] = field_counts.get(record.field, 0) + 1
                reviewer_counts[record.reviewer_id] = reviewer_counts.get(record.reviewer_id, 0) + 1

        return {
            "total_overlays": total_overlays,
            "tweets_with_overlays": tweets_with_overlays,
            "field_distribution": field_counts,
            "reviewer_distribution": reviewer_counts
        }

    def clear_overlays_for_tweet(self, tweet_id: str) -> int:
        """
        Remove all overlays for a specific tweet.

        Args:
            tweet_id: Tweet identifier

        Returns:
            Number of overlays removed
        """
        self._ensure_loaded()

        removed_count = len(self._overlays.get(tweet_id, []))
        if tweet_id in self._overlays:
            del self._overlays[tweet_id]
            self._save_overlays()
            logger.info(f"Cleared {removed_count} overlays for tweet {tweet_id}")

        return removed_count


# Global instance
_overlay_service = None

def get_overlay_service() -> OverlayService:
    """Get or create the global overlay service instance."""
    global _overlay_service
    if _overlay_service is None:
        _overlay_service = OverlayService()
    return _overlay_service