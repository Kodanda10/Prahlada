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

# Expanded semantic theme space (English -> Hindi)
ALLOWED_THEMES = [
    "Politics", "Governance", "Development", "Infrastructure",
    "Employment", "Economy", "Industry", "Welfare", "Security",
    "Culture", "Health", "Education", "Agriculture",
    "Environment", "Disaster", "Sports", "Tourism",
    "Technology", "SocialJustice", "WomenChild", "Finance",
    "Transport", "Housing", "Water", "Sanitation", "Climate", "Innovation", "Schemes"
]

THEME_MAP = {
    'Politics': 'राजनीति',
    'Governance': 'शासन',
    'Development': 'विकास',
    'Infrastructure': 'बुनियादी ढांचा',
    'Employment': 'रोजगार',
    'Economy': 'अर्थव्यवस्था',
    'Industry': 'उद्योग',
    'Welfare': 'कल्याण',
    'Security': 'सुरक्षा',
    'Culture': 'संस्कृति',
    'Health': 'स्वास्थ्य',
    'Education': 'शिक्षा',
    'Agriculture': 'कृषि',
    'Environment': 'पर्यावरण',
    'Disaster': 'आपदा',
    'Sports': 'खेल',
    'Tourism': 'पर्यटन',
    'Technology': 'प्रौद्योगिकी',
    'SocialJustice': 'सामाजिक न्याय',
    'WomenChild': 'महिला एवं बाल',
    'Finance': 'वित्त',
    'Transport': 'परिवहन',
    'Housing': 'आवास',
    'Water': 'पानी',
    'Sanitation': 'स्वच्छता',
    'Climate': 'जलवायु',
    'Innovation': 'नवाचार',
    'Schemes': 'योजनाएं'
}


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
        theme_options = ", ".join(ALLOWED_THEMES)
        return f"""Analyze this Hindi tweet and return concise reasoning.
Tweet: "{tweet_text}"

Output MUST be in Hindi terms for all lists and follow the 7-layer model:
1) Domain: up to 4 from [{theme_options}] (use Hindi equivalents in output)
2) Occasion/Ritual
3) Action Type
4) Relationship work
5) Strategic function
6) Emotional tone
7) Target audience
Also list: People, Organizations/Parties, Locations, Schemes, Event (short label), Confidence (0-1).

Response Format (plain text):
Summary: <text>
Domain: <item1>; <item2>
Occasion: <item1>; <item2>
Action: <item1>; <item2>
Relationship: <item1>; <item2>
Strategy: <item1>; <item2>
Emotion: <item1>; <item2>
Audience: <item1>; <item2>
People: <name1>; <name2>
Organizations: <org1>; <org2>
Locations: <loc1>; <loc2>
Schemes: <scheme1>; <scheme2>
Event: <label>
Confidence: <0-1>
"""
    
    async def _call_phi_async(self, prompt: str) -> dict:
        """
        Call Phi adapter asynchronously.
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.phi_adapter.client.generate(
                prompt=prompt,
                system_prompt="You are an expert analyst of Hindi government tweets.",
                json_mode=False
            )
        )
        
        # Handle response
        if isinstance(result, dict) and 'response' in result:
            return {'text': result['response']}
        elif isinstance(result, str):
            return {'text': result}
        return {'text': ''}
    
    def _parse_phi_reasoning(self, response: dict, tweet_text: str) -> TweetReasoning:
        """
        Parse Phi's text response using regex.
        """
        text = response.get('text', '')
        logger.info(f"Raw Phi Output: {text}")
        
        summary = ""
        themes = []
        locations = []
        people = []
        orgs = []
        event_label = ""
        schemes = []
        domain = []
        occasion = []
        action = []
        relationship = []
        strategy = []
        emotion = []
        audience = []
        
        # Extract Summary
        import re
        summary_match = re.search(r'Summary:\s*(.+)', text, re.IGNORECASE)
        if summary_match:
            summary = summary_match.group(1).strip()
            
        def _split_list(val: str) -> List[str]:
            return [v.strip() for v in re.split(r'[;,]', val) if v and v.strip()]

        # Extract Domain themes
        domain_match = re.search(r'Domain:\s*(.+)', text, re.IGNORECASE)
        if domain_match:
            domain = _split_list(domain_match.group(1))

        # Extract layers
        occ_match = re.search(r'Occasion:\s*(.+)', text, re.IGNORECASE)
        if occ_match:
            occasion = _split_list(occ_match.group(1))

        act_match = re.search(r'Action:\s*(.+)', text, re.IGNORECASE)
        if act_match:
            action = _split_list(act_match.group(1))

        rel_match = re.search(r'Relationship:\s*(.+)', text, re.IGNORECASE)
        if rel_match:
            relationship = _split_list(rel_match.group(1))

        strat_match = re.search(r'Strategy:\s*(.+)', text, re.IGNORECASE)
        if strat_match:
            strategy = _split_list(strat_match.group(1))

        emo_match = re.search(r'Emotion:\s*(.+)', text, re.IGNORECASE)
        if emo_match:
            emotion = _split_list(emo_match.group(1))

        aud_match = re.search(r'Audience:\s*(.+)', text, re.IGNORECASE)
        if aud_match:
            audience = _split_list(aud_match.group(1))

        # Extract locations/people/event where available
        loc_match = re.search(r'Locations?:\s*(.+)', text, re.IGNORECASE)
        if loc_match:
            locations = [loc.strip() for loc in re.split(r'[;,]', loc_match.group(1)) if loc.strip()]

        people_match = re.search(r'People?:\s*(.+)', text, re.IGNORECASE)
        if people_match:
            people = [p.strip() for p in re.split(r'[;,]', people_match.group(1)) if p.strip()]

        org_match = re.search(r'Organizations?:\s*(.+)', text, re.IGNORECASE)
        if org_match:
            orgs = [o.strip() for o in re.split(r'[;,]', org_match.group(1)) if o.strip()]

        scheme_match = re.search(r'Schemes?:\s*(.+)', text, re.IGNORECASE)
        if scheme_match:
            schemes = [s.strip() for s in re.split(r'[;,]', scheme_match.group(1)) if s.strip()]

        event_match = re.search(r'Event:\s*(.+)', text, re.IGNORECASE)
        if event_match:
            event_label = event_match.group(1).strip()
            
        # Normalize themes: allow Hindi or English, map to Hindi
        def _normalize_theme_list(values: List[str]) -> List[str]:
            out = []
            for v in values:
                if not v:
                    continue
                # Direct mapping for English keys
                if v in THEME_MAP:
                    out.append(THEME_MAP[v])
                else:
                    # If value already Hindi or unrecognized, keep as-is
                    out.append(v)
            return self._dedup(out)

        themes_hindi = _normalize_theme_list(domain)

        return TweetReasoning(
            contextual_summary=summary,
            implied_themes=themes_hindi,
            location_hints={},
            location_reasoning="",
            event_nuance=event_label,
            event_confidence=0.5,
            confidence=0.8 if themes else 0.5,
            reasoning_trace=text,
            people_entities=people,
            org_entities=orgs,
            location_entities=locations,
            scheme_entities=schemes,
            occasion_tags=self._dedup(occasion),
            action_tags=self._dedup(action),
            relationship_signals=self._dedup(relationship),
            strategy_signals=self._dedup(strategy),
            emotion_tags=self._dedup(emotion),
            audience_targets=self._dedup(audience)
        )
    
    def extract_semantic_buckets(self, reasoning: TweetReasoning) -> List[str]:
        """
        Extract semantic word buckets from Phi's reasoning and translate to Hindi.
        
        Uses Phi's implied_themes as semantic buckets.
        """
        return self._dedup(reasoning.implied_themes)

    @staticmethod
    def _dedup(seq: List[str]) -> List[str]:
        seen = set()
        out = []
        for item in seq:
            if not item:
                continue
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out

    def merge_word_buckets(self, semantic_buckets: List[str], original_data: dict, reasoning: Optional[TweetReasoning] = None) -> List[str]:
        """
        Combine semantic themes with tweet-specific entities (event, locations, people).
        """
        combined = list(semantic_buckets)

        event_type = original_data.get("event_type")
        if event_type:
            combined.append(str(event_type).strip())

        locations = original_data.get("locations") or []
        combined.extend([loc.strip() for loc in locations if isinstance(loc, str)])

        people = original_data.get("people") or original_data.get("people_mentioned") or []
        combined.extend([p.strip() for p in people if isinstance(p, str)])

        orgs = original_data.get("organizations") or []
        combined.extend([o.strip() for o in orgs if isinstance(o, str)])

        communities = original_data.get("communities") or []
        combined.extend([c.strip() for c in communities if isinstance(c, str)])

        schemes = original_data.get("schemes") or []
        combined.extend([s.strip() for s in schemes if isinstance(s, str)])

        if reasoning:
            combined.extend(self._dedup(reasoning.people_entities))
            combined.extend(self._dedup(reasoning.org_entities))
            combined.extend(self._dedup(reasoning.location_entities))
            combined.extend(self._dedup(reasoning.scheme_entities))
            combined.extend(self._dedup(reasoning.occasion_tags))
            combined.extend(self._dedup(reasoning.action_tags))
            combined.extend(self._dedup(reasoning.relationship_signals))
            combined.extend(self._dedup(reasoning.strategy_signals))
            combined.extend(self._dedup(reasoning.emotion_tags))
            combined.extend(self._dedup(reasoning.audience_targets))

        # Include geo hierarchy with Hindi labels if available
        loc_detail = original_data.get("location_detail") or {}
        def add_loc(label_key: str, value_key: str):
            val = loc_detail.get(value_key)
            if val:
                combined.append(f"{label_key}: {val}")

        add_loc("जिला", "district")
        add_loc("विधानसभा", "assembly")
        add_loc("संसदीय", "parliamentary")
        add_loc("ब्लॉक", "block")
        add_loc("ग्राम पंचायत", "gp")
        add_loc("गाँव", "village")
        add_loc("नगर", "ulb")
        add_loc("वार्ड", "ward")
        add_loc("ज़ोन", "zone")
        add_loc("स्थान", "canonical")

        hierarchy_path = original_data.get("hierarchy_path") or loc_detail.get("hierarchy_path") or []
        for node in hierarchy_path:
            if node:
                combined.append(f"पदानुक्रम: {node}")

        return self._dedup(combined)
    
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
        semantic_buckets = self.extract_semantic_buckets(reasoning)
        enriched["semantic_word_buckets"] = self.merge_word_buckets(
            semantic_buckets,
            original_data,
            reasoning
        )
        
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
            
            # Detailed log for audit (themes/entities)
            logger.info(
                f"[ENRICH] {tweet_id} themes={reasoning.implied_themes} "
                f"people={getattr(reasoning, 'people_entities', [])} "
                f"orgs={getattr(reasoning, 'org_entities', [])} "
                f"locs={getattr(reasoning, 'location_entities', [])} "
                f"schemes={getattr(reasoning, 'scheme_entities', [])}"
            )
            
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
