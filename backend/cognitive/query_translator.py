import json
from typing import Dict, Any, Optional
from ..core.logging import get_logger
from .phi_adapter import get_phi_adapter

logger = get_logger(__name__)

class QueryTranslator:
    """
    Translates Natural Language Queries into Structured Search Queries.
    Uses Phi 3.5 to extract intent, filters, and vector search terms.
    """
    
    def __init__(self):
        self.phi = get_phi_adapter()
        
    def translate(self, user_query: str) -> Dict[str, Any]:
        """
        Translate NL query to structured query.
        
        Returns:
            Dict with:
            - vector_query: str (for semantic search)
            - filters: Dict (sql filters like date, location)
            - limit: int
        """
        if not self.phi.enabled:
            # Fallback: Simple pass-through
            return {
                "vector_query": user_query,
                "filters": {},
                "limit": 10
            }
            
        prompt = self._build_prompt(user_query)
        
        try:
            response = self.phi.client.generate(prompt)
            structured = self._parse_response(response)
            return structured
        except Exception as e:
            logger.error(f"Query translation failed: {e}")
            # Fallback
            return {
                "vector_query": user_query,
                "filters": {},
                "limit": 10
            }
            
    def _build_prompt(self, query: str) -> str:
        return f"""
You are a Query Translator for a Tweet Knowledge Base.
Convert the user's natural language question into a structured JSON query.

Supported Filters:
- location: City or District name (e.g., "Raipur", "Bastar")
- event_type: "Political", "Cultural", "Development", "Other"
- date_range: "last_week", "last_month", "today", or specific "YYYY-MM-DD"

User Question: "{query}"

Respond ONLY with valid JSON:
{{
    "vector_query": "Key semantic terms for search",
    "filters": {{
        "location": "...",
        "event_type": "...",
        "date_range": "..."
    }},
    "limit": 10
}}
"""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        try:
            # Clean markdown
            cleaned = response.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse Phi response as JSON")
            return {"vector_query": "", "filters": {}, "limit": 10}

_query_translator = None

def get_query_translator() -> QueryTranslator:
    global _query_translator
    if _query_translator is None:
        _query_translator = QueryTranslator()
    return _query_translator
