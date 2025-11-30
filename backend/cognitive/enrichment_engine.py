"""
Phi 3.5 Enrichment Engine

Holistic tweet analysis and semantic enrichment pipeline.
Uses Phi to generate contextual understanding, then enriches parsed data.
"""
import asyncio
import logging
import json
from typing import Optional, Dict, List
from datetime import datetime

from .phi_adapter import get_phi_adapter
from .enrichment_schemas import TweetReasoning, EnrichmentResult

logger = logging.getLogger(__name__)


class PhiEnrichmentEngine:
    """
    Phi-powered semantic enrichment engine.
    
    Two-step process:
    1. Generate contextual reasoning (Phi reads tweet holistically)
    2. Enrich semantic fields using that reasoning
    """
    
    def __init__(self, timeout: int = 60):
        """
        Initialize enrichment engine.
        
        Args:
            timeout: Timeout in seconds for Phi calls
        """
        self.timeout = timeout
        self.phi_adapter = get_phi_adapter()
        
    async def generate_tweet_reasoning(
        self, 
        tweet_text: str,
        tweet_id: str
    ) -> Optional[TweetReasoning]:
        """
        Step 1: Generate Phi's contextual understanding of the tweet.
        
        Phi reads the tweet and generates human-like reasoning about:
        - What is the tweet about? (contextual summary)
        - What themes/topics are implied? (semantic buckets)
        - Where is this happening? (location validation)
        - What kind of event is this? (event classification)
        
        Args:
            tweet_text: The Hindi tweet text
            tweet_id: Tweet identifier for logging
            
        Returns:
            TweetReasoning object or None on failure
        """
        try:
            # Check if Phi adapter is available
            if not self.phi_adapter or not self.phi_adapter.client:
                logger.warning(f"Phi adapter not available for tweet {tweet_id}, skipping")
                return None
            
            # Build comprehensive prompt for Phi
            prompt = self._build_reasoning_prompt(tweet_text)
            
            # Call Phi with timeout
            response = await asyncio.wait_for(
                self._call_phi_async(prompt),
                timeout=self.timeout
            )
            
            # Parse Phi's response into TweetReasoning
            reasoning = self._parse_phi_reasoning(response, tweet_text)
            
            logger.info(f"Generated reasoning for tweet {tweet_id}: confidence={reasoning.confidence:.2f}")
            return reasoning
            
        except asyncio.TimeoutError:
            logger.error(f"Phi timeout for tweet {tweet_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to generate reasoning for {tweet_id}: {e}")
            return None
    
    def _build_reasoning_prompt(self, tweet_text: str) -> str:
        """
        Build comprehensive prompt for Phi to generate reasoning.
        
        Prompts Phi to:
        1. Understand tweet context
        2. Identify themes
        3. Validate location
        4. Classify event
        """
        return f"""You are analyzing a Hindi government tweet from Chhattisgarh. Read the tweet carefully and provide comprehensive reasoning.

Tweet: "{tweet_text}"

Provide the following analysis:

1. CONTEXTUAL SUMMARY (in English):
   - What is this tweet about in simple terms?
   - What is the main message or announcement?

2. IMPLIED THEMES (semantic buckets):
   - List key themes/topics (e.g., कृषि, स्वास्थ्य, शिक्षा, बुनियादी_ढांचा, etc.)
   - Focus on semantic meaning, not just keywords

3. LOCATION ANALYSIS:
   - What location(s) are mentioned or implied?
   - Confidence level (0-1) for each location
   - Reasoning for location identification

4. EVENT CLASSIFICATION:
   - What type of event is this? (e.g., बैठक, उद्घाटन, दौरा, etc.)
   - Any nuance or sub-type?
   - Confidence level (0-1)

5. OVERALL CONFIDENCE:
   - How confident are you in this analysis? (0-1)

Respond in JSON format:
{{
  "contextual_summary": "...",
  "implied_themes": ["theme1", "theme2"],
  "location_hints": {{"location": confidence}},
  "location_reasoning": "...",
  "event_nuance": "...",
  "event_confidence": 0.0,
  "confidence": 0.0,
  "reasoning_trace": "..."
}}"""
    
    async def _call_phi_async(self, prompt: str) -> dict:
        """
        Call Phi adapter asynchronously.
        
        Wraps synchronous Phi call in async executor for timeout support.
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.phi_adapter.client.generate(
                prompt=prompt,
                system_prompt="You are an expert analyst of Hindi government tweets. Provide thoughtful, accurate analysis.",
                json_mode=True
            )
        )
        
        # Phi returns: {'response': '{json...}', 'model': '...', ...}
        # We need to extract and parse the 'response' field
        if isinstance(result, dict) and 'response' in result:
            response_str = result['response']
            try:
                # First try: direct JSON parse
                parsed = json.loads(response_str)
                logger.debug(f"Parsed Phi response: {parsed}")
                return parsed
            except json.JSONDecodeError as e:
                # Phi sometimes returns mixed content like "{ ...text... }"
                # Try to extract JSON object/array from the response
                logger.warning(f"Failed to parse Phi response JSON (attempt 1): {response_str[:100]}...")
                
                # Try to find JSON object boundaries
                try:
                    # Look for first { and last }
                    if '{' in response_str and '}' in response_str:
                        start = response_str.index('{')
                        end = response_str.rindex('}') + 1
                        json_str = response_str[start:end]
                        parsed = json.loads(json_str)
                        logger.info(f"Recovered JSON from mixed content")
                        return parsed
                except (json.JSONDecodeError, ValueError) as e2:
                    logger.warning(f"Could not recover JSON from response, using defaults")
                    return {}
                return {}
        elif isinstance(result, str):
            # Fallback: try to parse as JSON string directly
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Phi response as JSON string")
                return {}
        elif isinstance(result, dict):
            # Already a dict (shouldn't happen with current Ollama client)
            return result
        else:
            logger.warning(f"Unexpected Phi response type: {type(result)}")
            return {}
    
    def _parse_phi_reasoning(self, response: dict, tweet_text: str) -> TweetReasoning:
        """
        Parse Phi's JSON response into TweetReasoning object.
        
        Handles missing fields with defaults.
        """
        return TweetReasoning(
            contextual_summary=response.get("contextual_summary", ""),
            implied_themes=response.get("implied_themes", []),
            location_hints=response.get("location_hints", {}),
            location_reasoning=response.get("location_reasoning", ""),
            event_nuance=response.get("event_nuance", ""),
            event_confidence=float(response.get("event_confidence", 0.5)),
            confidence=float(response.get("confidence", 0.5)),
            reasoning_trace=response.get("reasoning_trace", "")
        )
    
    def extract_semantic_buckets(self, reasoning: TweetReasoning) -> List[str]:
        """
        Extract semantic word buckets from Phi's reasoning.
        
        Uses Phi's implied_themes as semantic buckets.
        """
        return reasoning.implied_themes
    
    def enrich_from_reasoning(
        self, 
        original_data: dict,
        reasoning: TweetReasoning
    ) -> dict:
        """
        Step 2: Enrich parsed data using Phi's reasoning.
        
        Takes original parsed data and enriches it with:
        - Semantic word buckets from themes
        - Location corrections/validations
        - Event type refinements
        
        Args:
            original_data: Original parsed tweet data
            reasoning: Phi's contextual reasoning
            
        Returns:
            Enriched data dictionary (original + enrichments)
        """
        enriched = original_data.copy()
        
        # Add semantic word buckets
        enriched["semantic_word_buckets"] = self.extract_semantic_buckets(reasoning)
        
        # Location corrections (if Phi has high-confidence hints)
        location_corrections = {}
        for loc, conf in reasoning.location_hints.items():
            # Ensure confidence is a float, handle None
            try:
                confidence_float = float(conf) if (conf is not None) else 0.0
            except (ValueError, TypeError):
                confidence_float = 0.0
            
            if confidence_float > 0.75:  # High confidence threshold
                location_corrections[loc] = {
                    "confidence": confidence_float,  # Store as float
                    "reasoning": reasoning.location_reasoning
                }
        enriched["location_corrections"] = location_corrections
        
        # Event corrections (if Phi has nuanced classification)
        event_corrections = {}
        # First check if event_confidence exists and is not None
        if reasoning.event_confidence is not None:
            try:
                event_conf = float(reasoning.event_confidence)
            except (ValueError, TypeError):
                event_conf = 0.0
                
            if event_conf > 0.7:
                event_corrections["nuance"] = reasoning.event_nuance
                event_corrections["confidence"] = event_conf  # Store as float
        enriched["event_corrections"] = event_corrections
        
        # Store full reasoning for audit trail
        enriched["phi_reasoning"] = reasoning.to_dict()
        
        return enriched
    
    async def enrich_tweet(
        self,
        tweet_id: str,
        tweet_text: str,
        original_data: dict
    ) -> EnrichmentResult:
        """
        Full enrichment pipeline for a single tweet.
        
        Args:
            tweet_id: Tweet identifier
            tweet_text: Raw tweet text
            original_data: Original parsed data
            
        Returns:
            EnrichmentResult with success/failure status
        """
        try:
            # Step 1: Generate reasoning
            reasoning = await self.generate_tweet_reasoning(tweet_text, tweet_id)
            
            if reasoning is None:
                return EnrichmentResult(
                    tweet_id=tweet_id,
                    original_data=original_data,
                    reasoning=None,
                    semantic_word_buckets=[],
                    location_corrections={},
                    event_corrections={},
                    vector_embedding_id=None,
                    success=False,
                    error_message="Failed to generate Phi reasoning"
                )
            
            # Step 2: Enrich from reasoning
            enriched = self.enrich_from_reasoning(original_data, reasoning)
            
            return EnrichmentResult(
                tweet_id=tweet_id,
                original_data=original_data,
                reasoning=reasoning,
                semantic_word_buckets=enriched.get("semantic_word_buckets", []),
                location_corrections=enriched.get("location_corrections", {}),
                event_corrections=enriched.get("event_corrections", {}),
                vector_embedding_id=None,  # TODO: Generate embedding
                success=True
            )
            
        except Exception as e:
            logger.error(f"Enrichment failed for {tweet_id}: {e}")
            return EnrichmentResult(
                tweet_id=tweet_id,
                original_data=original_data,
                reasoning=None,
                semantic_word_buckets=[],
                location_corrections={},
                event_corrections={},
                vector_embedding_id=None,
                success=False,
                error_message=str(e)
            )
