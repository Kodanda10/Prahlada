"""
Phi 3.5 Local LM Adapter for Project Prahlada.

Provides advisory cognitive suggestions for tweet parsing enhancements.
Phi 3.5 serves as an intelligent assistant but NEVER modifies core parser logic.

Key Principles:
- Advisory only: Suggestions are reviewed by humans before application
- Non-destructive: Never overwrites canonical parsed data
- Structured output: Returns well-formed suggestion objects
- Graceful degradation: Works without Phi 3.5 in test/production scenarios
"""

import json
import logging
from typing import Dict, Any, List, Optional
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class PhiSuggestions:
    """Structured suggestion object from Phi 3.5."""

    def __init__(
        self,
        event_type_suggestions: Optional[List[str]] = None,
        sub_event_type: Optional[str] = None,
        location_candidates: Optional[List[Dict[str, Any]]] = None,
        scheme_suggestions: Optional[List[str]] = None,
        word_bucket_corrections: Optional[List[str]] = None, # V3.1
        entity_corrections: Optional[Dict[str, str]] = None, # V3.1
        cognitive_view: Optional[Dict[str, Any]] = None, # V5.0
        suggested_corrections: Optional[Dict[str, Any]] = None, # V5.0
        confidence_score: float = 0.0,
        reasoning: str = "",
        raw_response: Optional[str] = None
    ):
        self.event_type_suggestions = event_type_suggestions or []
        self.sub_event_type = sub_event_type
        self.location_candidates = location_candidates or []
        self.scheme_suggestions = scheme_suggestions or []
        self.word_bucket_corrections = word_bucket_corrections or []
        self.entity_corrections = entity_corrections or {}
        self.cognitive_view = cognitive_view or {}
        self.suggested_corrections = suggested_corrections or {}
        self.confidence_score = confidence_score
        self.reasoning = reasoning
        self.raw_response = raw_response

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_type_suggestions": self.event_type_suggestions,
            "sub_event_type": self.sub_event_type,
            "location_candidates": self.location_candidates,
            "scheme_suggestions": self.scheme_suggestions,
            "word_bucket_corrections": self.word_bucket_corrections,
            "entity_corrections": self.entity_corrections,
            "cognitive_view": self.cognitive_view,
            "suggested_corrections": self.suggested_corrections,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "raw_response": self.raw_response
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhiSuggestions':
        """Create from dictionary."""
        return cls(
            event_type_suggestions=data.get("event_type_suggestions", []),
            sub_event_type=data.get("sub_event_type"),
            location_candidates=data.get("location_candidates", []),
            scheme_suggestions=data.get("scheme_suggestions", []),
            word_bucket_corrections=data.get("word_bucket_corrections", []),
            entity_corrections=data.get("entity_corrections", {}),
            cognitive_view=data.get("cognitive_view", {}),
            suggested_corrections=data.get("suggested_corrections", {}),
            confidence_score=data.get("confidence_score", 0.0),
            reasoning=data.get("reasoning", ""),
            raw_response=data.get("raw_response")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_type_suggestions": self.event_type_suggestions,
            "sub_event_type": self.sub_event_type,
            "location_candidates": self.location_candidates,
            "scheme_suggestions": self.scheme_suggestions,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "raw_response": self.raw_response
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhiSuggestions':
        """Create from dictionary."""
        return cls(
            event_type_suggestions=data.get("event_type_suggestions", []),
            sub_event_type=data.get("sub_event_type"),
            location_candidates=data.get("location_candidates", []),
            scheme_suggestions=data.get("scheme_suggestions", []),
            confidence_score=data.get("confidence_score", 0.0),
            reasoning=data.get("reasoning", ""),
            raw_response=data.get("raw_response")
        )


class PhiAdapter:
    """
    Adapter for Phi 3.5 local language model.

    Provides structured suggestions for tweet parsing enhancements.
    All suggestions are advisory and require human review.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gemma2:9b",
        backup_model: str = "phi3.5",
        enabled: bool = True
    ):
        """
        Initialize LLM adapter (currently using Gemma 2:9b).

        Args:
            base_url: Ollama server URL
            model: Primary model name (gemma2:9b)
            backup_model: Fallback model
            enabled: Whether to use LLM enrichment (can be disabled for testing)
        """
        self.enabled = enabled
        self.model_name = model
        self.client = OllamaClient(
            base_url=base_url,
            model=model,
            backup_model=backup_model
        ) if enabled else None

        logger.info(f"LLM adapter initialized with {model}", extra={
            "enabled": enabled,
            "model": model,
            "backup_model": backup_model
        })

    def get_suggestions(self, tweet_id: str, raw_tweet: str, current_parsed: Dict[str, Any], context_examples: List[Dict[str, Any]] = None) -> PhiSuggestions:
        """
        Get cognitive suggestions from Phi 3.5.
        
        Args:
            tweet_id: Unique ID of the tweet
            raw_tweet: The original tweet text
            current_parsed: The current parsing result from V2
            context_examples: Optional list of similar past tweets/knowledge for few-shot learning
            
        Returns:
            PhiSuggestions object with structured advice
        """
        if not self.enabled or not self.client:
            logger.debug("Phi 3.5 disabled, returning empty suggestions")
            return PhiSuggestions()

        try:
            # Build prompt
            prompt = self._build_correction_prompt(raw_tweet, current_parsed, context_examples)

            logger.debug("Requesting Phi 3.5 suggestions", extra={"tweet_id": tweet_id})

            response = self.client.generate(
                prompt=prompt,
                system_prompt=self._get_correction_system_prompt(),
                json_mode=True
            )

            if "error" in response:
                logger.warning("Phi 3.5 correction request failed", extra={
                    "tweet_id": tweet_id,
                    "error": response["error"]
                })
                return PhiSuggestions()

            # Parse structured response
            suggestions = self._parse_correction_response(response["response"])
            suggestions.raw_response = response["response"]

            logger.info("Phi 3.5 suggestions generated", extra={
                "tweet_id": tweet_id,
                "confidence": suggestions.confidence_score,
                "suggestion_count": len(suggestions.event_type_suggestions)
            })

            return suggestions

        except Exception as e:
            logger.error("Phi 3.5 suggestion generation failed", extra={
                "tweet_id": tweet_id,
                "error": str(e)
            })
            raise ExternalServiceError(
                service="phi_3_5",
                reason=f"Suggestion generation failed: {str(e)}"
            )

    def suggest_geo_disambiguation(
        self,
        tweet_id: str,
        raw_tweet: str,
        location_candidates: List[str]
    ) -> PhiSuggestions:
        """
        Suggest disambiguation for location mentions.

        Args:
            tweet_id: Tweet identifier
            raw_tweet: Original tweet text
            location_candidates: Potential location strings

        Returns:
            PhiSuggestions with location ranking and disambiguation
        """
        if not self.enabled or not self.client:
            return PhiSuggestions()

        try:
            prompt = self._build_geo_prompt(raw_tweet, location_candidates)

            response = self.client.generate(
                prompt=prompt,
                system_prompt=self._get_geo_system_prompt(),
                json_mode=True
            )

            if "error" in response:
                logger.warning("Phi 3.5 geo disambiguation failed", extra={
                    "tweet_id": tweet_id,
                    "error": response["error"]
                })
                return PhiSuggestions()

            suggestions = self._parse_geo_response(response["response"])
            suggestions.raw_response = response["response"]

            return suggestions

        except Exception as e:
            logger.error("Phi 3.5 geo disambiguation failed", extra={
                "tweet_id": tweet_id,
                "error": str(e)
            })
            raise ExternalServiceError(
                service="phi_3_5",
                reason=f"Geo disambiguation failed: {str(e)}"
            )

    def rank_event_type_candidates(
        self,
        tweet_id: str,
        raw_tweet: str,
        candidates: List[str]
    ) -> PhiSuggestions:
        """
        Rank and suggest event type classifications.

        Args:
            tweet_id: Tweet identifier
            raw_tweet: Original tweet text
            candidates: Possible event type strings

        Returns:
            PhiSuggestions with ranked event type suggestions
        """
        if not self.enabled or not self.client:
            return PhiSuggestions()

        try:
            prompt = self._build_event_ranking_prompt(raw_tweet, candidates)

            response = self.client.generate(
                prompt=prompt,
                system_prompt=self._get_event_ranking_system_prompt(),
                json_mode=True
            )

            if "error" in response:
                logger.warning("Phi 3.5 event ranking failed", extra={
                    "tweet_id": tweet_id,
                    "error": response["error"]
                })
                return PhiSuggestions()

            suggestions = self._parse_event_ranking_response(response["response"])
            suggestions.raw_response = response["response"]

            return suggestions

        except Exception as e:
            logger.error("Phi 3.5 event ranking failed", extra={
                "tweet_id": tweet_id,
                "error": str(e)
            })
            raise ExternalServiceError(
                service="phi_3_5",
                reason=f"Event ranking failed: {str(e)}"
            )

    def check_health(self) -> bool:
        """
        Check if Phi 3.5 service is available.

        Returns:
            True if service is responding, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            return self.client.check_health()
        except Exception as e:
            logger.debug("Phi 3.5 health check failed", extra={"error": str(e)})
            return False

    def _build_correction_prompt(self, raw_tweet: str, current_parsed: Dict[str, Any], context_examples: List[Dict[str, Any]] = None) -> str:
        """
        Build prompt for Cognitive Knowledge Engine (V5.0).
        """
        context_section = ""
        if context_examples:
            context_section = "\n\nRelevant Past Knowledge (Use these as reference):\n"
            for i, ex in enumerate(context_examples):
                context_section += f"Example {i+1}:\n"
                context_section += f"- Text: {ex.get('text', '')[:100]}...\n"
                context_section += f"- Theme: {ex.get('themes', 'N/A')}\n"
                context_section += f"- Event Type: {ex.get('event_type', 'N/A')}\n"

        return f"""
Analyze this Hindi tweet as a Cognitive Engine.
Your goal is to extract structured knowledge, validate the parsing, and provide a rich cognitive view.
{context_section}

Tweet: "{raw_tweet}"

Current parsing result:
{json.dumps(current_parsed, indent=2, ensure_ascii=False)}

Please provide a JSON response with the following structure:

{{
    "reasoning": "Detailed step-by-step analysis of the tweet's intent, entities, and context.",
    
    "cognitive_view": {{
        "primary_theme": "Main theme (e.g., Tribal cultural recognition, Textile industry expansion)",
        "secondary_themes": ["Theme 2", "Theme 3"],
        "sector_tags": ["textiles", "fashion", "education", "infrastructure", "culture"],
        "stakeholders": {{
            "people": [{{ "name": "Name", "role": "Role", "inferred": true/false }}],
            "organizations": [{{ "name": "Org Name", "type": "Type" }}],
            "communities": [{{ "name": "Community Name", "type": "Type" }}]
        }},
        "event_context": {{
            "event_nature": "cultural/political/governance/economic/infrastructure/education/mixed",
            "is_cultural": true/false,
            "is_governance": true/false,
            "is_economic": true/false,
            "involves_scheme": true/false
        }},
        "scheme_and_programs": [{{ "name": "Scheme Name", "category": "Category" }}],
        "narrative_summary": "1-2 line plain English summary of what this tweet is really about.",
        "political_angle": "praise/critique/neutral/announcement/opposition-attack",
        "geo_context": {{
            "state": "State Name",
            "district": "District Name",
            "city_ulb": "City/ULB Name",
            "venue_type": "urban/rural"
        }}
    }},

    "word_bucket_corrections": ["High-signal word 1", "High-signal word 2"],
    
    "suggested_corrections": {{
        "event_type": {{ "suggested": "New Event Type", "reason": "Why" }},
        "sub_event_type": "Specific Sub-Event",
        "location": {{ "suggested": "New Location", "reason": "Why" }},
        "sector_tags_add": ["Tag 1", "Tag 2"]
    }},

    "confidence_score": 0.95
}}
"""

    def _build_geo_prompt(self, raw_tweet: str, location_candidates: List[str]) -> str:
        """Build prompt for geographic disambiguation."""
        candidates_str = ", ".join(f'"{loc}"' for loc in location_candidates)

        return f"""
Analyze this Hindi tweet and help disambiguate location mentions:

Tweet: "{raw_tweet}"

Potential locations mentioned: [{candidates_str}]

For each potential location, determine:
1. If it's a valid geographic location in India
2. The most likely intended location
3. Confidence in the identification

Respond in JSON format:
{{
    "location_candidates": [
        {{
            "original_text": "text from tweet",
            "resolved_name": "standardized location name",
            "confidence": 0.85,
            "location_type": "city|district|state|village",
            "context": "why this resolution"
        }}
    ],
    "confidence_score": 0.0,
    "reasoning": "Explanation of disambiguation decisions"
}}
"""

    def _build_event_ranking_prompt(self, raw_tweet: str, candidates: List[str]) -> str:
        """Build prompt for event type ranking."""
        candidates_str = ", ".join(f'"{event}"' for event in candidates)

        return f"""
Rank these event type classifications for this Hindi tweet:

Tweet: "{raw_tweet}"

Candidate event types: [{candidates_str}]

Determine which event types best describe this tweet.
Consider Indian context, government programs, and social issues.

Respond in JSON format:
{{
    "event_type_suggestions": ["best_match", "second_best", "third_best"],
    "confidence_score": 0.0,
    "reasoning": "Why these event types fit the tweet"
}}
"""

    def _get_correction_system_prompt(self) -> str:
        """System prompt for parser corrections."""
        return """You are an expert analyst of Indian government communications and social issues.
You help improve tweet parsing for better understanding of government schemes, protests, and public services.
Always provide structured, actionable suggestions that can be reviewed by human analysts.
Be conservative - only suggest high-confidence improvements."""

    def _get_geo_system_prompt(self) -> str:
        """System prompt for geographic disambiguation."""
        return """You are a geographic expert specializing in Indian locations.
You help disambiguate location mentions in Indian government and social context.
Consider administrative divisions: states, districts, cities, villages, and landmarks.
Be precise and conservative in your geographic identifications."""

    def _get_event_ranking_system_prompt(self) -> str:
        """System prompt for event type ranking."""
        return """You are an expert in classifying social and government events in India.
You understand the context of protests, government schemes, public services, and social issues.
Rank event types based on semantic fit and cultural/political context."""

    def _parse_correction_response(self, response: str) -> PhiSuggestions:
        """Parse correction response from Phi 3.5."""
        try:
            data = json.loads(response)
            
            # Extract suggestions from the new structure
            suggestions = data.get("suggested_corrections", {})
            event_type_sugg = []
            if suggestions.get("event_type"):
                event_type_sugg.append(suggestions["event_type"].get("suggested"))
                
            loc_candidates = []
            if suggestions.get("location"):
                loc_candidates.append({
                    "name": suggestions["location"].get("suggested"),
                    "confidence": 0.9,
                    "context": suggestions["location"].get("reason")
                })

            return PhiSuggestions(
                event_type_suggestions=event_type_sugg,
                sub_event_type=suggestions.get("sub_event_type"),
                location_candidates=loc_candidates,
                scheme_suggestions=[], # Handled in cognitive_view
                word_bucket_corrections=data.get("word_bucket_corrections", []),
                entity_corrections={}, # Handled in cognitive_view
                cognitive_view=data.get("cognitive_view", {}),
                suggested_corrections=data.get("suggested_corrections", {}),
                confidence_score=data.get("confidence_score", 0.0),
                reasoning=data.get("reasoning", "")
            )
        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse Phi 3.5 correction response", extra={
                "response": response[:200]
            })
            return PhiSuggestions()

    def _parse_geo_response(self, response: str) -> PhiSuggestions:
        """Parse geographic disambiguation response."""
        try:
            data = json.loads(response)
            return PhiSuggestions(
                location_candidates=data.get("location_candidates", []),
                confidence_score=data.get("confidence_score", 0.0),
                reasoning=data.get("reasoning", "")
            )
        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse Phi 3.5 geo response", extra={
                "response": response[:200]
            })
            return PhiSuggestions()

    def _parse_event_ranking_response(self, response: str) -> PhiSuggestions:
        """Parse event ranking response."""
        try:
            data = json.loads(response)
            return PhiSuggestions(
                event_type_suggestions=data.get("event_type_suggestions", []),
                confidence_score=data.get("confidence_score", 0.0),
                reasoning=data.get("reasoning", "")
            )
        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse Phi 3.5 event ranking response", extra={
                "response": response[:200]
            })
            return PhiSuggestions()


# Global instance for application use
_phi_adapter = None

def get_phi_adapter(**kwargs) -> Optional[PhiAdapter]:
    """
    Get the global Phi adapter instance.
    
    Uses lazy initialization to avoid blocking startup.
    Reads PHI_ENABLED environment variable (defaults to False for safety).
    """
    import os
    global _phi_adapter
    if _phi_adapter is None:
        # Read from environment - defaults to disabled for safety
        phi_enabled = os.getenv("PHI_ENABLED", "").lower() == "true"
        # Allow overriding model via env var, default to passed arg or gemma2:9b
        env_model = os.getenv("PHI_MODEL")
        default_model = kwargs.get("model", "gemma2:9b")
        model_name = env_model if env_model else default_model
        
        _phi_adapter = PhiAdapter(enabled=phi_enabled, model=model_name)
        if phi_enabled:
            logger.info(f"LLM enrichment enabled via PHI_ENABLED environment variable (using {model_name})")
    return _phi_adapter

def set_phi_adapter_config(
    enabled: bool = True,
    base_url: str = "http://localhost:11434",
    model: str = "gemma2:9b"
) -> None:
    """
    Configure the global Phi adapter.

    Call this during application startup with proper environment config.
    """
    global _phi_adapter
    _phi_adapter = PhiAdapter(
        enabled=enabled,
        base_url=base_url,
        model=model
    )