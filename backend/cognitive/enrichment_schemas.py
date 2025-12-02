"""
Schemas for Phi 3.5 Cognitive Enrichment Engine.

Defines data structures for capturing Phi's contextual reasoning
and semantic enrichment results.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class TweetReasoning:
    """
    Captures Phi 3.5's holistic understanding of a tweet.
    
    This is the "first step" - Phi reads the tweet and generates
    contextual understanding before any semantic extraction happens.
    """
    # Core Understanding
    contextual_summary: str  # Human-like summary of tweet intent
    implied_themes: List[str]  # Semantic word buckets/themes
    
    # Location Validation
    location_hints: Dict[str, float]  # {location_name: confidence}
    location_reasoning: str  # Why Phi thinks this is the location
    
    # Event Classification
    event_nuance: str  # Sub-type or specific detail
    event_confidence: float  # Confidence in classification
    
    # Overall Quality
    confidence: float  # Overall reasoning confidence (0-1)
    reasoning_trace: str  # Phi's thought process  

    # Extracted entities (optional)
    people_entities: List[str] = field(default_factory=list)
    org_entities: List[str] = field(default_factory=list)
    location_entities: List[str] = field(default_factory=list)
    scheme_entities: List[str] = field(default_factory=list)
    # Cognitive layers
    occasion_tags: List[str] = field(default_factory=list)
    action_tags: List[str] = field(default_factory=list)
    relationship_signals: List[str] = field(default_factory=list)
    strategy_signals: List[str] = field(default_factory=list)
    emotion_tags: List[str] = field(default_factory=list)
    audience_targets: List[str] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.utcnow)
    phi_model: str = "phi-3.5"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage."""
        return {
            "contextual_summary": self.contextual_summary,
            "implied_themes": self.implied_themes,
            "location_hints": self.location_hints,
            "location_reasoning": self.location_reasoning,
            "event_nuance": self.event_nuance,
            "event_confidence": self.event_confidence,
            "confidence": self.confidence,
            "reasoning_trace": self.reasoning_trace,
            "people_entities": self.people_entities,
            "org_entities": self.org_entities,
            "location_entities": self.location_entities,
            "scheme_entities": self.scheme_entities,
            "occasion_tags": self.occasion_tags,
            "action_tags": self.action_tags,
            "relationship_signals": self.relationship_signals,
            "strategy_signals": self.strategy_signals,
            "emotion_tags": self.emotion_tags,
            "audience_targets": self.audience_targets,
            "generated_at": self.generated_at.isoformat(),
            "phi_model": self.phi_model
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TweetReasoning':
        """Create from dictionary."""
        data = data.copy()
        if 'generated_at' in data and isinstance(data['generated_at'], str):
            data['generated_at'] = datetime.fromisoformat(data['generated_at'])
        # Backward compatibility defaults
        data.setdefault("people_entities", [])
        data.setdefault("org_entities", [])
        data.setdefault("location_entities", [])
        data.setdefault("scheme_entities", [])
        data.setdefault("occasion_tags", [])
        data.setdefault("action_tags", [])
        data.setdefault("relationship_signals", [])
        data.setdefault("strategy_signals", [])
        data.setdefault("emotion_tags", [])
        data.setdefault("audience_targets", [])
        return cls(**data)


@dataclass
class EnrichmentResult:
    """
    Result of enriching a tweet with Phi reasoning.
    
    Contains both the original data and the enriched semantic fields.
    """
    tweet_id: str
    original_data: dict
    reasoning: Optional[TweetReasoning]
    
    # Enriched Fields
    semantic_word_buckets: List[str]
    location_corrections: Dict[str, any]
    event_corrections: Dict[str, any]
    vector_embedding_id: Optional[str]
    
    # Status
    success: bool
    error_message: Optional[str] = None
    enrichment_version: str = "v1"
    enriched_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "tweet_id": self.tweet_id,
            "reasoning": self.reasoning.to_dict() if self.reasoning else None,
            "semantic_word_buckets": self.semantic_word_buckets,
            "location_corrections": self.location_corrections,
            "event_corrections": self.event_corrections,
            "vector_embedding_id": self.vector_embedding_id,
            "success": self.success,
            "error_message": self.error_message,
            "enrichment_version": self.enrichment_version,
            "enriched_at": self.enriched_at.isoformat()
        }
