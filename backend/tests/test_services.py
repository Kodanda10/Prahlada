"""
Unit tests for backend services.

Tests business logic in isolation from API endpoints.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.stats_service import StatsService
from backend.services.events_service import EventsService
from backend.services.ingest_service import IngestService
from backend.core.exceptions import DatabaseError, NotFoundError
from backend import schemas, models


class TestStatsService:
    """Unit tests for StatsService."""

    @pytest.fixture
    def mock_db(self):
        """Mock AsyncSession."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def stats_service(self, mock_db):
        """StatsService instance with mocked DB."""
        return StatsService(mock_db)

    @pytest.mark.asyncio
    async def test_get_tweet_stats_success(self, stats_service, mock_db):
        """Should return tweet statistics successfully."""
        # Mock the execute results
        mock_result_total = MagicMock()
        mock_result_total.scalar_one.return_value = 100
        mock_result_processed = MagicMock()
        mock_result_processed.scalar_one.return_value = 75
        mock_result_pending = MagicMock()
        mock_result_pending.scalar_one.return_value = 15
        mock_result_failed = MagicMock()
        mock_result_failed.scalar_one.return_value = 10

        mock_db.execute.side_effect = [
            mock_result_total,
            mock_result_processed,
            mock_result_pending,
            mock_result_failed,
        ]

        stats = await stats_service.get_tweet_stats()

        assert stats == {
            "total_tweets": 100,
            "parsed_success": 75,
            "pending": 15,
            "errors": 10,
        }

        # Verify correct queries were made
        assert mock_db.execute.call_count == 4

    @pytest.mark.asyncio
    async def test_get_tweet_stats_database_error(self, stats_service, mock_db):
        """Should raise DatabaseError on query failure."""
        mock_db.execute.side_effect = Exception("Database connection failed")

        with pytest.raises(DatabaseError) as exc_info:
            await stats_service.get_tweet_stats()

        assert "Failed to retrieve tweet statistics" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_processing_summary_with_rates(self, stats_service, mock_db):
        """Should calculate success/error rates correctly."""
        # Mock the execute results
        mock_result_total = MagicMock()
        mock_result_total.scalar_one.return_value = 200
        mock_result_processed = MagicMock()
        mock_result_processed.scalar_one.return_value = 160
        mock_result_pending = MagicMock()
        mock_result_pending.scalar_one.return_value = 20
        mock_result_failed = MagicMock()
        mock_result_failed.scalar_one.return_value = 20

        mock_db.execute.side_effect = [
            mock_result_total,
            mock_result_processed,
            mock_result_pending,
            mock_result_failed,
        ]

        summary = await stats_service.get_processing_summary()

        expected = {
            "total_tweets": 200,
            "parsed_success": 160,
            "pending": 20,
            "errors": 20,
            "success_rate": 80.0,
            "error_rate": 10.0,
            "pending_rate": 10.0,
        }
        assert summary == expected

    @pytest.mark.asyncio
    async def test_get_processing_summary_zero_tweets(self, stats_service, mock_db):
        """Should handle zero tweets gracefully."""
        # Mock zero results
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_db.execute.return_value = mock_result

        summary = await stats_service.get_processing_summary()

        expected = {
            "total_tweets": 0,
            "parsed_success": 0,
            "pending": 0,
            "errors": 0,
            "success_rate": 0.0,
            "error_rate": 0.0,
            "pending_rate": 0.0,
        }
        assert summary == expected


class TestEventsService:
    """Unit tests for EventsService."""

    @pytest.fixture
    def mock_db(self):
        """Mock AsyncSession."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def events_service(self, mock_db):
        """EventsService instance with mocked DB."""
        return EventsService(mock_db)

    @pytest.mark.asyncio
    async def test_get_events_success(self, events_service, mock_db):
        """Should return events successfully."""
        # Mock parsed event
        mock_parsed = MagicMock()
        mock_parsed.tweet_id = "tweet-123"
        mock_parsed.categories = {"event": ["demo"], "locations": ["Delhi"]}
        mock_parsed.event_type = "demo"
        mock_parsed.locations = ["Delhi"]
        mock_parsed.schemes_mentioned = ["PM-KISAN"]
        mock_parsed.parsed_at = MagicMock()
        mock_parsed.parsed_at.isoformat.return_value = "2024-01-01T00:00:00"

        # Mock raw tweet
        mock_raw = MagicMock()
        mock_raw.text = "Sample tweet text"
        mock_raw.created_at = MagicMock()
        mock_raw.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_raw.processing_status = "processed"

        # Mock query result
        mock_result = MagicMock()
        mock_result.all.return_value = [(mock_parsed, mock_raw)]
        mock_db.execute.return_value = mock_result

        events = await events_service.get_events()

        assert len(events) == 1
        event = events[0]
        assert event["tweet_id"] == "tweet-123"
        assert event["parsing_status"] == "SUCCESS"
        assert event["event_type"] == ["demo"]
        assert event["scheme_tags"] == ["PM-KISAN"]

    @pytest.mark.asyncio
    async def test_get_events_with_status_filter(self, events_service, mock_db):
        """Should filter events by status."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        events = await events_service.get_events(status="success")

        assert events == []
        # Verify the query was made with filtering
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_events_database_error(self, events_service, mock_db):
        """Should raise DatabaseError on query failure."""
        mock_db.execute.side_effect = Exception("Query failed")

        with pytest.raises(DatabaseError) as exc_info:
            await events_service.get_events()

        assert "Failed to retrieve events" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_event_by_id_found(self, events_service, mock_db):
        """Should return event if found."""
        mock_event = MagicMock()
        mock_db.get.return_value = mock_event

        result = await events_service.get_event_by_id("tweet-123")

        assert result == mock_event
        mock_db.get.assert_called_once_with(models.ParsedEvent, "tweet-123")

    @pytest.mark.asyncio
    async def test_get_event_by_id_not_found(self, events_service, mock_db):
        """Should return None if event not found."""
        mock_db.get.return_value = None

        result = await events_service.get_event_by_id("tweet-999")

        assert result is None

    @pytest.mark.asyncio
    async def test_approve_event_success(self, events_service, mock_db):
        """Should approve event successfully."""
        # Mock existing event
        mock_event = MagicMock()
        mock_db.get.return_value = mock_event

        result = await events_service.approve_event("tweet-123", "admin")

        assert result == {"status": "success", "message": "Event tweet-123 approved"}
        assert mock_event.review_status == "approved"
        assert mock_event.needs_review == False
        assert mock_event.reviewed_by == "admin"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_event_not_found(self, events_service, mock_db):
        """Should raise NotFoundError for non-existent event."""
        mock_db.get.return_value = None

        with pytest.raises(NotFoundError):
            await events_service.approve_event("tweet-999", "admin")

    @pytest.mark.asyncio
    async def test_approve_event_database_error(self, events_service, mock_db):
        """Should raise DatabaseError on commit failure."""
        mock_event = MagicMock()
        mock_db.get.return_value = mock_event
        mock_db.commit.side_effect = Exception("Commit failed")

        with pytest.raises(DatabaseError):
            await events_service.approve_event("tweet-123", "admin")

    def test_transform_event_with_categories(self, events_service):
        """Should transform event with categories correctly."""
        mock_parsed = MagicMock()
        mock_parsed.tweet_id = "tweet-123"
        mock_parsed.categories = {
            "event": ["demo", "rally"],
            "locations": ["Delhi", "Mumbai"],
            "schemes": ["PM-KISAN", "Ayushman Bharat"],
            "raw_text": "Original tweet",
            "clean_text": "Cleaned tweet",
        }
        mock_parsed.event_type = "demo"
        mock_parsed.locations = ["Delhi"]
        mock_parsed.schemes_mentioned = ["PM-KISAN"]
        mock_parsed.parsed_at = MagicMock()
        mock_parsed.parsed_at.isoformat.return_value = "2024-01-01T00:00:00"

        mock_raw = MagicMock()
        mock_raw.text = "Original tweet"
        mock_raw.created_at = MagicMock()
        mock_raw.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_raw.processing_status = "processed"

        result = events_service._transform_event(mock_parsed, mock_raw)

        assert result["tweet_id"] == "tweet-123"
        assert result["event_type"] == ["demo", "rally"]
        assert result["location_text"] == "Delhi, Mumbai"
        assert result["scheme_tags"] == ["PM-KISAN", "Ayushman Bharat"]
        assert result["parsing_status"] == "SUCCESS"

    def test_transform_event_empty_categories(self, events_service):
        """Should handle empty categories gracefully."""
        mock_parsed = MagicMock()
        mock_parsed.tweet_id = "tweet-456"
        mock_parsed.categories = {}
        mock_parsed.event_type = None
        mock_parsed.locations = None
        mock_parsed.schemes_mentioned = None
        mock_parsed.parsed_at = MagicMock()
        mock_parsed.parsed_at.isoformat.return_value = "2024-01-01T00:00:00"

        mock_raw = MagicMock()
        mock_raw.text = "Tweet text"
        mock_raw.created_at = MagicMock()
        mock_raw.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_raw.processing_status = "failed"

        result = events_service._transform_event(mock_parsed, mock_raw)

        assert result["tweet_id"] == "tweet-456"
        assert result["event_type"] == []
        assert result["location_text"] == "Unknown"
        assert result["scheme_tags"] == []
        assert result["parsing_status"] == "FAILED"


class TestIngestService:
    """Unit tests for IngestService."""

    @pytest.fixture
    def mock_db(self):
        """Mock AsyncSession."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def ingest_service(self, mock_db):
        """IngestService instance with mocked DB."""
        return IngestService(mock_db)

    @pytest.mark.asyncio
    async def test_ingest_parsed_tweet_new(self, ingest_service, mock_db):
        """Should ingest new tweet successfully."""
        # Mock no existing event
        mock_db.get.return_value = None

        # Mock schema payload
        payload = schemas.IngestPayload(
            tweet=schemas.TweetSchema(
                id="tweet-123",
                text="Sample tweet",
                created_at=MagicMock(),
                author_id="user-123"
            ),
            categories=schemas.IngestCategories(
                event=["demo"],
                locations=["Delhi"],
                schemes=["PM-KISAN"]
            ),
            gemini_metadata=schemas.IngestMetadata(
                model="gpt-4",
                confidence=0.85
            )
        )

        result = await ingest_service.ingest_parsed_tweet(payload)

        assert result == {
            "status": "success",
            "message": "Data for tweet tweet-123 ingested."
        }

        # Verify database operations (adds both ParsedEvent and RawTweet)
        assert mock_db.add.call_count == 2
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_ingest_parsed_tweet_duplicate(self, ingest_service, mock_db):
        """Should skip duplicate tweets."""
        # Mock existing event
        mock_existing = MagicMock()
        mock_db.get.return_value = mock_existing

        payload = schemas.IngestPayload(
            tweet=schemas.TweetSchema(
                id="tweet-123",
                text="Sample tweet",
                created_at=MagicMock(),
                author_id="user-123"
            ),
            categories=schemas.IngestCategories(),
            gemini_metadata=schemas.IngestMetadata(model="gpt-4", confidence=0.85)
        )

        result = await ingest_service.ingest_parsed_tweet(payload)

        assert result == {
            "status": "skipped",
            "message": "Parsed event already exists."
        }

        # Verify no new additions
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_ingest_parsed_tweet_database_error(self, ingest_service, mock_db):
        """Should raise DatabaseError on commit failure."""
        mock_db.get.return_value = None
        mock_db.commit.side_effect = Exception("Commit failed")

        payload = schemas.IngestPayload(
            tweet=schemas.TweetSchema(
                id="tweet-123",
                text="Sample tweet",
                created_at=MagicMock(),
                author_id="user-123"
            ),
            categories=schemas.IngestCategories(),
            gemini_metadata=schemas.IngestMetadata(model="gpt-4", confidence=0.85)
        )

        with pytest.raises(DatabaseError):
            await ingest_service.ingest_parsed_tweet(payload)

        # Verify rollback was called
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_exists_found(self, ingest_service, mock_db):
        """Should return True if event exists."""
        mock_event = MagicMock()
        mock_db.get.return_value = mock_event

        result = await ingest_service.check_exists("tweet-123")

        assert result is True
        mock_db.get.assert_called_once_with(models.ParsedEvent, "tweet-123")

    @pytest.mark.asyncio
    async def test_check_exists_not_found(self, ingest_service, mock_db):
        """Should return False if event doesn't exist."""
        mock_db.get.return_value = None

        result = await ingest_service.check_exists("tweet-999")

        assert result is False

    @pytest.mark.asyncio
    async def test_check_exists_database_error(self, ingest_service, mock_db):
        """Should raise DatabaseError on query failure."""
        mock_db.get.side_effect = Exception("Query failed")

        with pytest.raises(DatabaseError):
            await ingest_service.check_exists("tweet-123")