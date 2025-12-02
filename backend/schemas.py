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
    review_status: Optional[str] = None
    needs_review: Optional[bool] = None
    word_buckets: Optional[List[str]] = None
    parsed_data_v8: Optional[Dict[str, Any]] = None
    metadata_v8: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True # Replaces orm_mode = True

class EnrichedItemResponse(BaseModel):
    """
    Response model for enriched items.
    """
    tweet_id: str
    themes: Optional[List[str]] = []
    event_type: Optional[str] = None
    sentiment: Optional[str] = None
    location_candidates: Optional[Dict[str, Any]] = None
    schemes: Optional[List[str]] = []
    communities: Optional[List[str]] = []
    notes: Optional[str] = None
    confidence_score: float = 0.0
    model_version: Optional[str] = None
    enriched_at: datetime

    class Config:
        from_attributes = True

class GeoLocationResponse(BaseModel):
    """
    Response model for geo locations.
    """
    id: str
    name: str
    type: str
    parent_id: Optional[str] = None
    aliases: Optional[List[str]] = []
    metadata_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


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
    name: str
    data: Dict[str, Any]


class ApplyOverlayRequest(BaseModel):
    overlay_id: str


class ApplyOverlayResponse(BaseModel):
    status: str
    message: str


class OverlayHealthResponse(BaseModel):
    status: str
    query_performance_ms: float
    total_overlays: int
    tweets_with_overlays: int
    service_ready: bool


# --- Review Arbitration Schemas (Parser vs LLM) ---

class EngineOutput(BaseModel):
    """Output from either Parser or LLM for a single field."""
    value: Any
    confidence: float
    source: Optional[str] = None  # e.g., "keyword_match", "llm_reasoning"
    reasoning: Optional[str] = None  # LLM explanation

class FieldComparison(BaseModel):
    """Comparison of Parser vs LLM for a single field."""
    parser: EngineOutput
    llm: EngineOutput
    conflict: bool

class ComparisonResponse(BaseModel):
    """Full comparison object for a tweet."""
    tweet_id: str
    raw_text: str
    comparison: Dict[str, FieldComparison]

class AskAIRequest(BaseModel):
    """Request to Ask AI about a specific tweet."""
    tweet_id: str
    question: str

class AskAIResponse(BaseModel):
    """Response from Ask AI."""
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: float

class FieldFeedback(BaseModel):
    """Feedback for a single field."""
    choice: str  # 'parser_win', 'llm_win', 'mixed', 'manual'
    disagreement_strength: Optional[float] = None
    comment: Optional[str] = None

class ApprovalRequest(BaseModel):
    """Request to approve a tweet with arbitration feedback."""
    tweet_id: str
    final_data: Dict[str, Any]  # Golden record
    feedback: Dict[str, FieldFeedback]  # Per-field feedback
    session_id: Optional[str] = None
    review_time_sec: Optional[int] = None
    exclude_from_analytics: Optional[bool] = False

class SkipRequest(BaseModel):
    tweet_id: str
    reason: Optional[str] = None

