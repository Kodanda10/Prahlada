from sqlalchemy import (
    Column, String, DateTime, Text, JSON, Boolean, Float
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from .database import Base, DATABASE_URL
import datetime
import uuid

IS_SQLITE = DATABASE_URL.startswith("sqlite")
JSONType = JSON if IS_SQLITE else JSONB
ArrayType = JSON if IS_SQLITE else ARRAY(String)

# --- ORM Models for Project Dhruv ---
# These classes define the structure of our database tables.

class RawTweet(Base):
    """
    Model for the raw_tweets table, storing tweets as they are fetched.
    """
    __tablename__ = "raw_tweets"

    tweet_id = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    author_handle = Column(String)
    # Statuses: 'pending', 'processed', 'failed', 'pending_retry'
    processing_status = Column(String, default='pending', index=True)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


class ParsedEvent(Base):
    """

    Model for parsed_events, storing the structured data extracted from tweets.
    """
    __tablename__ = "parsed_events"

    id = Column(String, primary_key=True, index=True) # Using tweet_id as primary key
    tweet_id = Column(String, index=True, unique=True)
    
    # Categories extracted by the AI
    categories = Column(JSONType, nullable=True)
    
    # Metadata from the parsing process
    gemini_metadata = Column(JSONType, nullable=True)

    # Simplified top-level fields for quick querying
    event_type = Column(String, nullable=True)
    locations = Column(ArrayType, nullable=True)
    people_mentioned = Column(ArrayType, nullable=True)
    schemes_mentioned = Column(ArrayType, nullable=True)
    word_buckets = Column(ArrayType, nullable=True)
    organizations = Column(ArrayType, nullable=True)

    # V5: Cognitive Knowledge Engine Fields
    cognitive_view = Column(JSONType, nullable=True)
    quality_flags = Column(JSONType, nullable=True)

    # Review and confidence
    overall_confidence = Column(Float, default=0.0)
    needs_review = Column(Boolean, default=True)
    # Statuses: 'pending', 'approved', 'rejected', 'edited'
    review_status = Column(String, default='pending', index=True)
    
    parsed_at = Column(DateTime, default=datetime.datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)


class WordBucket(Base):
    """
    Model for the word_buckets table, storing high-signal terms and their clusters.
    """
    __tablename__ = "word_buckets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    term = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False) # sector, event, actor, etc.
    cluster_id = Column(String, index=True)
    language = Column(String, default="hi")
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AdminUser(Base):
    """
    Stores administrator credentials for dashboard access.
    """
    __tablename__ = "admin_users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    roles = Column(JSON, default=list)
    display_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
