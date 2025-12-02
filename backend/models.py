from sqlalchemy import (
    Column, String, DateTime, Text, JSON, Boolean, Float
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from .database import Base
import datetime
import uuid

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
    categories = Column(JSONB, nullable=True)
    
    # Metadata from the parsing process
    gemini_metadata = Column(JSONB, nullable=True)

    # Simplified top-level fields for quick querying
    event_type = Column(String, nullable=True)
    locations = Column(JSONB, nullable=True)
    people_mentioned = Column(ARRAY(String), nullable=True)
    schemes_mentioned = Column(ARRAY(String), nullable=True)
    word_buckets = Column(ARRAY(String), nullable=True)

    # Arbitration & Review (New for Parser vs LLM UI)
    final_data = Column(JSONB, nullable=True)  # Human-approved golden record (SSOT)
    feedback_log = Column(JSONB, nullable=True)  # Track parser_win/llm_win per field
    cognitive_view = Column(JSONB, nullable=True)  # LLM reasoning for Ask AI

    # Review and confidence
    overall_confidence = Column(Float, default=0.0)
    needs_review = Column(Boolean, default=True)
    # Statuses: 'pending', 'approved', 'rejected', 'edited'
    review_status = Column(String, default='pending', index=True)
    
    parsed_at = Column(DateTime, default=datetime.datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)


class EnrichedItem(Base):
    """
    Model for enriched_items, storing the deep analysis from Gemma 3.
    """
    __tablename__ = "enriched_items"

    tweet_id = Column(String, primary_key=True, index=True)
    
    # Core Enrichment Fields
    themes = Column(JSONB, nullable=True) # List of strings: ["विकास", "राष्ट्रवाद"]
    event_type = Column(String, nullable=True) # "रैली", "जनसभा"
    sentiment = Column(String, nullable=True) # "Positive", "Negative", "Neutral"
    
    # Detailed Extraction
    location_candidates = Column(JSONB, nullable=True) # Structured location info
    schemes = Column(ARRAY(String), nullable=True)
    communities = Column(ARRAY(String), nullable=True)
    people = Column(ARRAY(String), nullable=True)
    organizations = Column(ARRAY(String), nullable=True)
    
    # The 7-Layer Cognitive Model
    layers = Column(JSONB, nullable=True) # Stores Domain, Occasion, Action, Relationship, Strategy, Emotion, Audience
    
    # Narrative & Notes
    notes = Column(Text, nullable=True) # Hindi summary/notes
    confidence_score = Column(Float, default=0.0)
    
    # Metadata
    model_version = Column(String, nullable=True) # e.g., "gemma-3-qat-12b"
    enriched_at = Column(DateTime, default=datetime.datetime.utcnow)


class GeoLocation(Base):
    """
    Canonical catalogue of locations for normalization and mapping.
    """
    __tablename__ = "geo_locations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Hierarchy
    name = Column(String, nullable=False, index=True) # Canonical name (English/Hindi)
    type = Column(String, nullable=False, index=True) # State, District, AC, Block, GP
    parent_id = Column(String, nullable=True, index=True)
    
    # Search Helpers
    aliases = Column(ARRAY(String), nullable=True) # ["Raipur", "रायपुर"]
    vector_embedding = Column(ARRAY(Float), nullable=True) # For vector search
    
    # Metadata
    metadata_info = Column(JSONB, nullable=True) # Population, demographics, etc.



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
