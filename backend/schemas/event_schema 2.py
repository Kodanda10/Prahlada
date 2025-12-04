"""
Event Object Schema - Production-Ready
Full 5W1H structured data for instant NLQ responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LocationDetail(BaseModel):
    """Location hierarchy for events"""
    city: Optional[str] = None
    venue: Optional[str] = None
    district: Optional[str] = None
    assembly_constituency: Optional[str] = None
    state: str = "छत्तीसगढ़"


class EmploymentAnnouncement(BaseModel):
    """Employment/recruitment details"""
    posts: Optional[str] = None  # "20,000 नई भर्तियाँ"
    positions: Optional[List[str]] = None  # ["तहसीलदार", "पटवारी"]
    application_deadline: Optional[str] = None


class Announcements(BaseModel):
    """Financial and employment announcements"""
    amount: Optional[str] = None  # "₹5000 करोड़"
    employment: Optional[EmploymentAnnouncement] = None
    beneficiaries: Optional[str] = None  # "15 लाख किसान"
    timeline: Optional[str] = None  # "6 महीने में पूर्ण"


class Narrative(BaseModel):
    """Political and contextual narrative"""
    tags: List[str] = Field(default_factory=list)  # ["क्रांति", "India Model"]
    political_context: Optional[str] = None
    quotes: Optional[List[str]] = None  # Key quotes from leaders


class EventObject(BaseModel):
    """
    Complete event object with full 5W1H data.
    This is the single source of truth for NLQ responses.
    """
    # Identifiers
    event_id: str = Field(..., description="Unique event identifier")
    tweet_ids: List[str] = Field(default_factory=list)
    
    # Core Event Data
    scheme_name: str = Field(..., description="योजना/परियोजना का नाम")
    event_type: str = Field(..., description="scheme_launch, announcement, meeting, etc.")
    
    # 5W1H - WHEN
    event_date: Optional[str] = Field(None, description="YYYY-MM-DD format")
    event_time: Optional[str] = Field(None, description="HH:MM format")
    event_date_display: Optional[str] = None  # "14 जून 2024"
    
    # 5W1H - WHERE
    location: LocationDetail
    
    # 5W1H - WHO
    leaders_main: List[str] = Field(default_factory=list, description="मुख्य नेता/अधिकारी")
    leaders_others: List[str] = Field(default_factory=list, description="अन्य उपस्थित")
    
    # 5W1H - WHAT
    announcements: Optional[Announcements] = None
    objectives: List[str] = Field(default_factory=list)
    facilities: List[str] = Field(default_factory=list)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # 5W1H - HOW/CONTEXT
    narrative: Optional[Narrative] = None
    
    # Metadata
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Search/Index fields
    keywords_hindi: List[str] = Field(default_factory=list)
    keywords_english: List[str] = Field(default_factory=list)


class NLQResponse(BaseModel):
    """Standard NLQ API response"""
    query: str
    answer: str
    response_mode: str = Field(..., description="cache | event_object | rag_llm")
    quality_score: Optional[int] = None
    missing_fields: List[str] = Field(default_factory=list)
    response_time_seconds: float
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    event_objects_used: List[str] = Field(default_factory=list)
    confidence: float = 1.0


class QuerySpec(BaseModel):
    """
    Internal query specification for intent detection.
    Converts natural language to structured query.
    """
    entity_type: str = Field(..., description="scheme | event | leader | location")
    entity_name: str
    query_focus: List[str] = Field(default_factory=list)  # ["launch_details", "amount"]
    geo_focus: List[str] = Field(default_factory=list)
    time_focus: Optional[str] = None
    answer_fields: List[str] = Field(default_factory=list)
    language: str = "hi"
