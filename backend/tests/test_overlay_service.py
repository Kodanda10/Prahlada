"""
Tests for overlay service functionality.

Tests human-reviewed correction overlay system.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from backend.services.overlay_service import OverlayService, OverlayRecord, get_overlay_service


class TestOverlayRecord:
    """Tests for OverlayRecord data structure."""

    def test_overlay_record_creation(self):
        """Should create overlay record with required fields."""
        record = OverlayRecord(
            tweet_id="tweet-123",
            field="event_type",
            corrected_value="rally",
            reviewer_id="user-456",
            notes="Corrected from meeting to rally"
        )

        assert record.tweet_id == "tweet-123"
        assert record.field == "event_type"
        assert record.corrected_value == "rally"
        assert record.reviewer_id == "user-456"
        assert record.notes == "Corrected from meeting to rally"
        assert record.source == "human_review"
        assert record.confidence == 1.0
        assert "overlay_tweet-123_event_type_" in record.id

    def test_overlay_record_to_dict(self):
        """Should convert to dictionary correctly."""
        record = OverlayRecord(
            tweet_id="tweet-123",
            field="event_type",
            corrected_value="rally"
        )

        data = record.to_dict()

        required_fields = ["id", "tweet_id", "field", "corrected_value", "created_at"]
        for field in required_fields:
            assert field in data

        assert data["tweet_id"] == "tweet-123"
        assert data["field"] == "event_type"
        assert data["corrected_value"] == "rally"

    def test_overlay_record_from_dict(self):
        """Should create from dictionary correctly."""
        data = {
            "id": "overlay_test",
            "tweet_id": "tweet-123",
            "field": "event_type",
            "corrected_value": "rally",
            "reviewer_id": "user-456",
            "created_at": "2024-01-01T00:00:00"
        }

        record = OverlayRecord.from_dict(data)

        assert record.id == "overlay_test"
        assert record.tweet_id == "tweet-123"
        assert record.field == "event_type"
        assert record.corrected_value == "rally"
        assert record.reviewer_id == "user-456"


class TestOverlayService:
    """Tests for OverlayService functionality."""

    @pytest.fixture
    def temp_overlay_dir(self, tmp_path):
        """Create temporary directory for overlay storage."""
        overlay_dir = tmp_path / "overlays"
        overlay_dir.mkdir()
        return overlay_dir

    @pytest.fixture
    def overlay_service(self, temp_overlay_dir):
        """OverlayService instance with temporary storage."""
        return OverlayService(str(temp_overlay_dir))

    def test_add_overlay(self, overlay_service):
        """Should add overlay successfully."""
        record = overlay_service.add_overlay(
            tweet_id="tweet-123",
            field="event_type",
            corrected_value="rally",
            reviewer_id="user-456",
            notes="Human correction"
        )

        assert isinstance(record, OverlayRecord)
        assert record.tweet_id == "tweet-123"
        assert record.field == "event_type"
        assert record.corrected_value == "rally"
        assert record.reviewer_id == "user-456"
        assert record.notes == "Human correction"

    def test_get_overlays_for_tweet(self, overlay_service):
        """Should retrieve overlays for specific tweet."""
        # Add multiple overlays
        overlay_service.add_overlay("tweet-123", "event_type", "rally")
        overlay_service.add_overlay("tweet-123", "location", "Delhi")
        overlay_service.add_overlay("tweet-456", "event_type", "protest")

        overlays_123 = overlay_service.get_overlays_for_tweet("tweet-123")
        overlays_456 = overlay_service.get_overlays_for_tweet("tweet-456")
        overlays_999 = overlay_service.get_overlays_for_tweet("tweet-999")

        assert len(overlays_123) == 2
        assert len(overlays_456) == 1
        assert len(overlays_999) == 0

        fields_123 = {o.field for o in overlays_123}
        assert fields_123 == {"event_type", "location"}

    def test_apply_overlays_no_overlays(self, overlay_service):
        """Should return original data when no overlays exist."""
        original_data = {
            "event_type": "meeting",
            "location": "Conference Hall",
            "schemes": []
        }

        result = overlay_service.apply_overlays(original_data, "tweet-123")

        assert result == original_data

    def test_apply_overlays_with_corrections(self, overlay_service):
        """Should apply approved overlays to parsed data."""
        # Add overlays
        overlay_service.add_overlay("tweet-123", "event_type", "rally", confidence=0.9)
        overlay_service.add_overlay("tweet-123", "location", "Delhi", confidence=0.8)

        original_data = {
            "event_type": "meeting",
            "location": "Conference Hall",
            "schemes": []
        }

        result = overlay_service.apply_overlays(original_data, "tweet-123")

        # Should have applied corrections
        assert result["event_type"] == "rally"
        assert result["location"] == "Delhi"
        assert result["schemes"] == []  # Unchanged

        # Original should be unchanged
        assert original_data["event_type"] == "meeting"

    def test_apply_overlays_low_confidence_ignored(self, overlay_service):
        """Should ignore low-confidence overlays."""
        # Add low-confidence overlay
        overlay_service.add_overlay("tweet-123", "event_type", "rally", confidence=0.5)

        original_data = {"event_type": "meeting"}

        result = overlay_service.apply_overlays(original_data, "tweet-123")

        # Should not apply low-confidence overlay
        assert result["event_type"] == "meeting"

    def test_persistence_save_and_load(self, temp_overlay_dir):
        """Should persist overlays to disk and reload them."""
        # Create service and add overlays
        service1 = OverlayService(str(temp_overlay_dir))
        service1.add_overlay("tweet-123", "event_type", "rally")
        service1.add_overlay("tweet-123", "location", "Delhi")

        # Create new service instance (simulates restart)
        service2 = OverlayService(str(temp_overlay_dir))
        overlays = service2.get_overlays_for_tweet("tweet-123")

        assert len(overlays) == 2
        fields = {o.field for o in overlays}
        values = {o.corrected_value for o in overlays}
        assert fields == {"event_type", "location"}
        assert values == {"rally", "Delhi"}

    def test_clear_overlays_for_tweet(self, overlay_service):
        """Should clear all overlays for a specific tweet."""
        # Add overlays
        overlay_service.add_overlay("tweet-123", "event_type", "rally")
        overlay_service.add_overlay("tweet-123", "location", "Delhi")
        overlay_service.add_overlay("tweet-456", "event_type", "protest")

        # Clear overlays for tweet-123
        removed_count = overlay_service.clear_overlays_for_tweet("tweet-123")

        assert removed_count == 2
        assert len(overlay_service.get_overlays_for_tweet("tweet-123")) == 0
        assert len(overlay_service.get_overlays_for_tweet("tweet-456")) == 1

    def test_get_overlay_stats(self, overlay_service):
        """Should provide overlay statistics."""
        # Add overlays from different reviewers
        overlay_service.add_overlay("tweet-123", "event_type", "rally", reviewer_id="user1")
        overlay_service.add_overlay("tweet-123", "location", "Delhi", reviewer_id="user1")
        overlay_service.add_overlay("tweet-456", "event_type", "protest", reviewer_id="user2")

        stats = overlay_service.get_overlay_stats()

        assert stats["total_overlays"] == 3
        assert stats["tweets_with_overlays"] == 2
        assert stats["field_distribution"]["event_type"] == 2
        assert stats["field_distribution"]["location"] == 1
        assert stats["reviewer_distribution"]["user1"] == 2
        assert stats["reviewer_distribution"]["user2"] == 1

    def test_multiple_overlays_same_field(self, overlay_service):
        """Should handle multiple overlays for same field (use latest approved)."""
        # Add multiple overlays for same field
        overlay_service.add_overlay("tweet-123", "event_type", "meeting", confidence=0.6)
        overlay_service.add_overlay("tweet-123", "event_type", "rally", confidence=0.9)  # Higher confidence

        original_data = {"event_type": "gathering"}

        result = overlay_service.apply_overlays(original_data, "tweet-123")

        # Should apply the higher confidence overlay
        assert result["event_type"] == "rally"

    def test_overlay_service_isolation(self, overlay_service):
        """Should isolate overlays between different tweets."""
        overlay_service.add_overlay("tweet-123", "event_type", "rally")
        overlay_service.add_overlay("tweet-456", "event_type", "protest")

        data_123 = {"event_type": "meeting"}
        data_456 = {"event_type": "gathering"}

        result_123 = overlay_service.apply_overlays(data_123, "tweet-123")
        result_456 = overlay_service.apply_overlays(data_456, "tweet-456")

        assert result_123["event_type"] == "rally"
        assert result_456["event_type"] == "protest"

        # Originals unchanged
        assert data_123["event_type"] == "meeting"
        assert data_456["event_type"] == "gathering"