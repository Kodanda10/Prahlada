from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- Pydantic Schemas for API Validation ---
# These models define the expected data shapes for API requests and responses.

class TweetSchema(BaseModel):
    id: str
    text: str
    created_at: datetime
    author_id: str

class IngestCategories(BaseModel):
    locations: Optional[List[str]] = []
    people: Optional[List[str]] = []
    event: Optional[List[str]] = []
    organisation: Optional[List[str]] = []
    schemes: Optional[List[str]] = []
    communities: Optional[List[str]] = []

class IngestMetadata(BaseModel):
    model: str
    confidence: float
    # Allow any other fields to be present
    class Config:
        extra = 'allow'

class IngestPayload(BaseModel):
    """
    Defines the structure of the data sent from the Node.js ingestion script.
    """
    tweet: TweetSchema
    categories: IngestCategories
    gemini_metadata: IngestMetadata

class StatsResponse(BaseModel):
    """
    Response model for the /api/stats endpoint.
    """
    total_tweets: int
    parsed_success: int
    pending: int
    errors: int

class EventResponse(BaseModel):
    """
    Response model for individual events in the /api/events list.
    """
    tweet_id: str
    created_at: datetime
    raw_text: str
    clean_text: str
    event_type: List[str]
    location_text: str
    scheme_tags: List[str]
    parsing_status: str
    logs: List[str]

    class Config:
        from_attributes = True # Replaces orm_mode = True

class AnalyticsDataPoint(BaseModel):
    name: str
    value: int

class VectorIndexTriggerPayload(BaseModel):
    tweetIds: List[str]


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, serialize_by_alias=True)

    id: str
    username: str
    roles: List[str] = Field(default_factory=list)
    display_name: Optional[str] = Field(default=None, serialization_alias="displayName")
    email: Optional[str] = None


class AuthResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    token: str
    user: AuthUser

class CorrectionRequest(BaseModel):
    tweet_id: str
    text: str
    old_data: Dict[str, Any]
    correction: Dict[str, Any]

class CorrectionResponse(BaseModel):
    status: str
    log_id: Optional[str] = None
    decision: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    k: int = 10

class SearchResult(BaseModel):
    tweet_id: str
    text: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class TelemetryRequest(BaseModel):
    type: str
    name: str
    data: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    timestamp: Optional[int] = None

class EventUpdateRequest(BaseModel):
    parsed_data: Dict[str, Any]

class AddOverlayRequest(BaseModel):
    tweet_id: str
    field: str
    corrected_value: Any
    reviewer_id: str
    reviewer_name: Optional[str] = None
    notes: Optional[str] = None

class ApplyOverlayRequest(BaseModel):
    tweet_id: str
    parsed_data: Dict[str, Any]

class ApplyOverlayResponse(BaseModel):
    status: str
    corrected_data: Dict[str, Any]
    applied_overlays: int

class OverlayHealthResponse(BaseModel):
    status: str
    query_performance_ms: float
    total_overlays: int
    tweets_with_overlays: int
    service_ready: bool

