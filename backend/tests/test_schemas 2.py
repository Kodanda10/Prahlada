"""
Backend Pydantic schema tests.
Tests data validation for all API request/response schemas.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from backend.schemas import (
    TweetSchema,
    AuthRequest,
    AuthResponse,
    AuthUser,
    SearchRequest,
    SearchResult,
    StatsResponse,
    IngestPayload,
    IngestCategories,
    IngestMetadata,
    TelemetryRequest,
    EventUpdateRequest,
)


class TestTweetSchema:
    """Test TweetSchema validation."""
    
    def test_valid_tweet_schema(self):
        """Valid tweet data should parse successfully."""
        tweet = TweetSchema(
            id="123456789",
            text="Tweet content here",
            created_at=datetime.utcnow(),
            author_id="user123",
        )
        
        assert tweet.id == "123456789"
        assert tweet.text == "Tweet content here"
        assert tweet.author_id == "user123"
    
    def test_tweet_schema_missing_required(self):
        """Missing required fields should raise ValidationError."""
        with pytest.raises(ValidationError):
            TweetSchema(
                id="123",
                # missing text, created_at, author_id
            )


class TestAuthSchemas:
    """Test auth-related schemas."""
    
    def test_auth_request_valid(self):
        """Valid auth request should parse."""
        req = AuthRequest(username="admin", password="secret")
        
        assert req.username == "admin"
        assert req. password == "secret"
    
    def test_auth_request_missing_password(self):
        """Missing password should fail."""
        with pytest.raises(ValidationError):
            AuthRequest(username="admin")
    
    def test_auth_user_schema(self):
        """AuthUser schema should parse correctly."""
        user = AuthUser(
            id="user123",
            username="testuser",
            roles=["admin", "editor"],
            display_name="Test User",
            email="test@example.com",
        )
        
        assert user.username == "testuser"
        assert "admin" in user.roles
        assert user.display_name == "Test User"
    
    def test_auth_response_schema(self):
        """AuthResponse should contain token and user."""
        user = AuthUser(
            id="123",
            username="admin",
            roles=["admin"],
        )
        
        response = AuthResponse(
            token="jwt_token_here",
            user=user,
        )
        
        assert response.token == "jwt_token_here"
        assert response.user.username == "admin"


class TestSearchSchemas:
    """Test search-related schemas."""
    
    def test_search_request_defaults(self):
        """SearchRequest should have default k value."""
        req = SearchRequest(query="test query")
        
        assert req.query == "test query"
        assert req.k == 10  # default
    
    def test_search_request_custom_k(self):
        """Custom k value should be accepted."""
        req = SearchRequest(query="search", k=20)
        
        assert req.k == 20
    
    def test_search_result_schema(self):
        """SearchResult should parse correctly."""
        result = SearchResult(
            tweet_id="987",
            text="Matching tweet",
            score=0.95,
            metadata={"category": "event"},
        )
        
        assert result.score == 0.95
        assert result.metadata["category"] == "event"


class TestStatsResponse:
    """Test stats response schema."""
    
    def test_stats_response_valid(self):
        """Stats response with all fields."""
        stats = StatsResponse(
            total_tweets=1000,
            parsed_success=900,
            pending=50,
            errors=50,
        )
        
        assert stats.total_tweets == 1000
        assert stats.parsed_success == 900


class TestIngestSchemas:
    """Test data ingestion schemas."""
    
    def test_ingest_categories_defaults(self):
        """Categories should default to empty lists."""
        cats = IngestCategories()
        
        assert cats.locations == []
        assert cats.people == []
        assert cats.schemes == []
    
    def test_ingest_categories_with_data(self):
        """Categories should accept list data."""
        cats = IngestCategories(
            locations=["रायपुर", "बिलासपुर"],
            people=["मुख्यमंत्री"],
            event=["दौरा"],
        )
        
        assert len(cats.locations) == 2
        assert "मुख्यमंत्री" in cats.people
    
    def test_ingest_metadata_schema(self):
        """Metadata should parse with extra fields."""
        metadata = IngestMetadata(
            model="gemini-2.0",
            confidence=0.92,
            # Extra fields allowed
        )
        
        assert metadata.model == "gemini-2.0"
        assert metadata.confidence == 0.92
    
    def test_ingest_payload_complete(self):
        """Complete ingestion payload should parse."""
        tweet = TweetSchema(
            id="123",
            text="Content",
            created_at=datetime.utcnow(),
            author_id="author1",
        )
        
        categories = IngestCategories(locations=["Location1"])
        metadata = IngestMetadata(model="test", confidence=0.8)
        
        payload = IngestPayload(
            tweet=tweet,
            categories=categories,
            gemini_metadata=metadata,
        )
        
        assert payload.tweet.id == "123"
        assert "Location1" in payload.categories.locations


class TestEventUpdateRequest:
    """Test event update request schema."""
    
    def test_event_update_request(self):
        """Event update request should accept parsed_data dict."""
        req = EventUpdateRequest(
            parsed_data={
                "event_type": "दौरा",
                "location": "रायपुर",
                "confidence": 0.9,
            }
        )
        
        assert req.parsed_data["event_type"] == "दौरा"
        assert req.parsed_data["confidence"] == 0.9


class TestTelemetryRequest:
    """Test telemetry request schema."""
    
    def test_telemetry_request_complete(self):
        """Complete telemetry request should parse."""
        req = TelemetryRequest(
            type="event",
            name="user_action",
            data={"action": "click", "target": "button"},
            url="/dashboard",
            timestamp=1234567890,
        )
        
        assert req.type == "event"
        assert req.name == "user_action"
        assert req.data["action"] == "click"
    
    def test_telemetry_request_optional_fields(self):
        """Telemetry without optional fields should parse."""
        req = TelemetryRequest(
            type="pageview",
            name="home",
        )
        
        assert req.type == "pageview"
        assert req.data is None
        assert req.url is None
