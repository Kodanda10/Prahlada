"""
SQLite-compatible SQLAlchemy models for backend testing.

These models mirror the production models but use SQLite-compatible types
instead of PostgreSQL-specific types (JSONB, ARRAY).

Note: Class names use 'Mock' prefix to avoid pytest collection warnings.
"""

from sqlalchemy import (
    Column, String, DateTime, Text, JSON, Boolean, Float
)
from sqlalchemy.orm import declarative_base
import datetime
import uuid

# Separate base for test models
MockBase = declarative_base()


class MockRawTweet(MockBase):
    """
    SQLite-compatible model for raw_tweets table.
    """
    __tablename__ = "raw_tweets"

    tweet_id = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    author_handle = Column(String)
    processing_status = Column(String, default='pending', index=True)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


class MockParsedEvent(MockBase):
    """
    SQLite-compatible model for parsed_events table.
    Uses JSON instead of JSONB, and JSON for arrays instead of ARRAY.
    """
    __tablename__ = "parsed_events"

    id = Column(String, primary_key=True, index=True)
    tweet_id = Column(String, index=True, unique=True)
    
    # Use JSON instead of JSONB for SQLite compatibility
    categories = Column(JSON, nullable=True)
    gemini_metadata = Column(JSON, nullable=True)

    event_type = Column(String, nullable=True)
    # Use JSON instead of ARRAY for SQLite compatibility
    locations = Column(JSON, nullable=True)
    people_mentioned = Column(JSON, nullable=True)
    schemes_mentioned = Column(JSON, nullable=True)

    overall_confidence = Column(Float, default=0.0)
    needs_review = Column(Boolean, default=True)
    review_status = Column(String, default='pending', index=True)
    
    parsed_at = Column(DateTime, default=datetime.datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)


class MockAdminUser(MockBase):
    """
    SQLite-compatible model for admin_users table.
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
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
