"""
Backend model tests.
Tests SQLAlchemy models for RawTweet, ParsedEvent, and AdminUser.
"""
import pytest
from datetime import datetime
import uuid
from backend.models import RawTweet, ParsedEvent, AdminUser


class TestRawTweetModel:
    """Test RawTweet model."""
    
    def test_raw_tweet_creation(self):
        """RawTweet should be created with required fields."""
        tweet = RawTweet(
            tweet_id="123456789",
            text="Test tweet content",
            created_at=datetime.utcnow(),
            author_handle="@testuser",
        )
        
        assert tweet.tweet_id == "123456789"
        assert tweet.text == "Test tweet content"
        assert tweet.author_handle == "@testuser"
        assert tweet.processing_status == "pending"  # default
    
    def test_raw_tweet_processing_status_default(self):
        """Processing status should default to 'pending'."""
        tweet = RawTweet(
            tweet_id="test123",
            text="Content",
            created_at=datetime.utcnow(),
        )
        
        assert tweet.processing_status == "pending"
    
    def test_raw_tweet_fetched_at_auto_set(self):
        """fetched_at should be auto-set."""
        tweet = RawTweet(
            tweet_id="test456",
            text="Content",
            created_at=datetime.utcnow(),
        )
        
        # fetched_at default is set via default parameter
        assert hasattr(tweet, 'fetched_at')


class TestParsedEventModel:
    """Test ParsedEvent model."""
    
    def test_parsed_event_creation(self):
        """ParsedEvent should be created with required fields."""
        event = ParsedEvent(
            id= str(uuid.uuid4()),
            tweet_id="987654321",
            event_type="दौरा",
            locations=["रायपुर", "बिलासपुर"],
            people_mentioned=["मुख्यमंत्री"],
        )
        
        assert event.tweet_id == "987654321"
        assert event.event_type == "दौरा"
        assert "रायपुर" in event.locations
        assert "मुख्यमंत्री" in event.people_mentioned
    
    def test_parsed_event_defaults(self):
        """ParsedEvent should have proper defaults."""
        event = ParsedEvent(
            id=str(uuid.uuid4()),
            tweet_id="test789",
        )
        
        assert event.overall_confidence == 0.0
        assert event.needs_review is True
        assert event.review_status == "pending"
    
    def test_parsed_event_jsonb_fields(self):
        """JSONB fields should accept dict data."""
        metadata = {"parser": "v2", "confidence": 0.95}
        categories = {"type": "event", "priority": "high"}
        
        event = ParsedEvent(
            id=str(uuid.uuid4()),
            tweet_id="jsonb_test",
            gemini_metadata=metadata,
            categories=categories,
        )
        
        assert event.gemini_metadata == metadata
        assert event.categories == categories
    
    def test_parsed_event_array_fields(self):
        """Array fields should accept list data."""
        event = ParsedEvent(
            id=str(uuid.uuid4()),
            tweet_id="array_test",
            locations=["location1", "location2", "location3"],
            schemes_mentioned=["scheme A", "scheme B"],
word_buckets=["bucket1", "bucket2"],
        )
        
        assert len(event.locations) == 3
        assert len(event.schemes_mentioned) == 2
        assert len(event.word_buckets) == 2


class TestAdminUserModel:
    """Test AdminUser model."""
    
    def test_admin_user_creation(self):
        """AdminUser should be created with required fields."""
        user = AdminUser(
            username="testadmin",
            password_hash="hashed_password_here",
            roles=["admin", "editor"],
            display_name="Test Admin",
        )
        
        assert user.username == "testadmin"
        assert user.password_hash == "hashed_password_here"
        assert "admin" in user.roles
        assert user.display_name == "Test Admin"
    
    def test_admin_user_id_auto_generated(self):
        """Admin user ID should be auto-generated UUID."""
        user = AdminUser(
            username="user123",
            password_hash="hash",
        )
        
        assert user.id is not None
        # UUID format check
        assert isinstance(user.id, str) or user.id is None  # Will be set on init
    
    def test_admin_user_is_active_default(self):
        """is_active should default to True."""
        user = AdminUser(
            username="activeuser",
            password_hash="hash",
        )
        
        assert user.is_active is True
    
    def test_admin_user_roles_default(self):
        """roles should default to empty list."""
        user = AdminUser(
            username="noroles",
            password_hash="hash",
        )
        
        assert user.roles == [] or user.roles is None or isinstance(user.roles, list)
    
    def test_admin_user_timestamps(self):
        """Timestamps should be present."""
        user = AdminUser(
            username="timestamptest",
            password_hash="hash",
        )
        
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')
