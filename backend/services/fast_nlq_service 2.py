"""
Fast NLQ Service - 3-Tier Response System
Tier 1: Cache (10-50ms)
Tier 2: Event Object Template (500ms-1s)
Tier 3: RAG + LLM (optional, 50s+)
"""

import hashlib
import time
import re
from typing import Optional, Dict, Any, List
from backend.schemas.event_schema import EventObject, NLQResponse, QuerySpec
from backend.cognitive.event_objects import CRITICAL_EVENTS, get_event_by_scheme_name


class FastNLQService:
    """
    Production NLQ service with 3-tier response system.
    """
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache (replace with Redis in production)
        self.event_store = self._load_event_store()
    
    def _load_event_store(self) -> Dict[str, EventObject]:
        """Load all event objects into memory for fast lookup"""
        from backend.schemas.event_schema import EventObject
        from backend.services.event_loader import get_all_events_sync
        
        print("🔄 Loading event objects from database...")
        
        # Load from database (includes critical events + enriched items)
        all_events = get_all_events_sync()
        
        store = {}
        for event_data in all_events:
            try:
                event = EventObject(**event_data)
                store[event.event_id] = event
                
                # Also index by scheme name (lowercase, normalized)
                if event.scheme_name and event.scheme_name != "Unknown Event":
                    scheme_key = event.scheme_name.lower().replace(" ", "_")
                    # Only overwrite if higher confidence
                    if scheme_key not in store or event.confidence > store[scheme_key].confidence:
                        store[scheme_key] = event
                
                # Index by keywords
                for keyword in event.keywords_hindi:
                    kw_key = keyword.lower().replace(" ", "_")
                    if kw_key not in store or event.confidence > store.get(kw_key, event).confidence:
                        store[kw_key] = event
                        
            except Exception as e:
                print(f"⚠️ Error loading event {event_data.get('event_id')}: {e}")
                continue
        
        print(f"✅ Loaded {len(all_events)} events into NLQ store ({len(store)} total indices)")
        return store
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for cache key"""
        # Remove extra spaces, punctuation
        normalized = re.sub(r'[^\w\s]', '', query.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _detect_intent(self, query: str) -> Optional[QuerySpec]:
        """
        Simple intent detection - match query to known entities.
        In production, use a small classifier or regex patterns.
        """
        query_lower = query.lower()
        
        # Detect scheme mentions
        scheme_patterns = {
            "भूमि सुधार": "bhumi_sudhar_launch",
            "नवा रायपुर": "nava_raipur_cfc",
            "common facility": "nava_raipur_cfc",
            "अंजोर vision": "chhattisgarh_anjor_vision_2047",
            "vision 2047": "chhattisgarh_anjor_vision_2047"
        }
        
        for pattern, event_id in scheme_patterns.items():
            if pattern in query_lower:
                return QuerySpec(
                    entity_type="scheme",
                    entity_name=event_id,
                    query_focus=["launch_details", "5w1h"],
                    answer_fields=["date", "location", "leaders", "amount"]
                )
        
        return None
    
    def _build_template_answer(self, event: EventObject) -> str:
        """
        Generate templated answer from event object.
        Fast, structured, NO LLM needed.
        """
        parts = []
        
        # Saar (Summary)
        parts.append(f"**📋 सार**\n{event.scheme_name} - {event.event_type}")
        
        # 5W1H विवरण
        details = ["**📍 5W1H विवरण**"]
        
        if event.event_date:
            date_display = event.event_date_display or event.event_date
            details.append(f"• **कब:** {date_display}")
        
        if event.location:
            loc_parts = []
            if event.location.venue:
                loc_parts.append(event.location.venue)
            if event.location.city:
                loc_parts.append(event.location.city)
            if event.location.district:
                loc_parts.append(f"{event.location.district} जिला")
            details.append(f"• **कहाँ:** {', '.join(loc_parts)}")
        
        if event.leaders_main:
            details.append(f"• **किसने:** {', '.join(event.leaders_main)}")
        
        if event.leaders_others:
            details.append(f"• **किनके साथ:** {', '.join(event.leaders_others[:3])}")  # Top 3
        
        if event.announcements:
            if event.announcements.amount:
                details.append(f"• **राशि:** {event.announcements.amount}")
            if event.announcements.employment and event.announcements.employment.posts:
                details.append(f"• **रोजगार:** {event.announcements.employment.posts}")
            if event.announcements.beneficiaries:
                details.append(f"• **लाभार्थी:** {event.announcements.beneficiaries}")
        
        if event.narrative and event.narrative.political_context:
            details.append(f"• **संदर्भ:** {event.narrative.political_context}")
        
        parts.append("\n".join(details))
        
        # Objectives
        if event.objectives:
            parts.append(f"\n**💡 मुख्य बिंदु**\n" + "\n".join(f"• {obj}" for obj in event.objectives[:3]))
        
        # Milestones (for timeline queries)
        if event.milestones:
            parts.append(f"\n**📅 Timeline**\n" + "\n".join(
                f"• {m.get('year')}: {m.get('target')}" for m in event.milestones[:3]
            ))
        
        # Tags
        if event.narrative and event.narrative.tags:
            parts.append(f"\n🏷️ **Tags**: {', '.join(event.narrative.tags)}")
        
        return "\n\n".join(parts)
    
    async def answer_query(
        self,
        query: str,
        use_llm_polish: bool = False,
        force_refresh: bool = False
    ) -> NLQResponse:
        """
        Main entry point - 3-tier response system.
        """
        start_time = time.time()
        cache_key = self._get_cache_key(query)
        
        # TIER 1: Cache Hit
        if not force_refresh and cache_key in self.cache:
            cached = self.cache[cache_key]
            cached.response_time_seconds = time.time() - start_time
            cached.response_mode = "cache"
            print(f"⚡ Cache HIT: {query[:50]}... ({cached.response_time_seconds*1000:.0f}ms)")
            return cached
        
        # TIER 2: Event Object Template
        intent = self._detect_intent(query)
        if intent and intent.entity_name in self.event_store:
            event = self.event_store[intent.entity_name]
            answer = self._build_template_answer(event)
            
            response = NLQResponse(
                query=query,
                answer=answer,
                response_mode="event_object",
                quality_score=4,  # Template is always high quality
                missing_fields=[],
                response_time_seconds=time.time() - start_time,
                event_objects_used=[event.event_id],
                confidence=event.confidence
            )
            
            # Cache it
            self.cache[cache_key] = response
            
            print(f"🎯 Event Object: {query[:50]}... ({response.response_time_seconds*1000:.0f}ms)")
            return response
        
        # TIER 3: RAG + LLM (fallback)
        if use_llm_polish:
            from backend.cognitive.nlq_engine import get_nlq_engine
            engine = get_nlq_engine()
            result = engine.answer_query(query)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(result['answer'], query)
            
            response = NLQResponse(
                query=query,
                answer=result['answer'],
                response_mode="rag_llm",
                quality_score=quality_score['score'],
                missing_fields=quality_score['missing'],
                response_time_seconds=time.time() - start_time,
                sources=result.get('sources', []),
                event_objects_used=[],
                confidence=0.7
            )
            
            # Cache it
            self.cache[cache_key] = response
            
            print(f"🧠 RAG+LLM: {query[:50]}... ({response.response_time_seconds:.1f}s)")
            return response
        
        # If LLM not requested and no event object found
        return NLQResponse(
            query=query,
            answer="इस प्रश्न के लिए हमारे पास अभी structured डेटा उपलब्ध नहीं है। कृपया प्रश्न को और स्पष्ट करें या 'detailed mode' सक्षम करें।",
            response_mode="not_found",
            quality_score=0,
            missing_fields=["all_data"],
            response_time_seconds=time.time() - start_time,
            confidence=0.0
        )
    
    def _calculate_quality_score(self, answer: str, query: str) -> Dict[str, Any]:
        """Calculate quality score for an answer"""
        score = 0
        missing = []
        
        # Date check
        if re.search(r'\d{4}|\d{1,2}\s+(जनवरी|फरवरी|मार्च|अप्रैल|मई|जून)', answer):
            score += 1
        else:
            missing.append('date')
        
        # Location check
        if re.search(r'रायपुर|बिलासपुर|नवा रायपुर', answer, re.IGNORECASE):
            score += 1
        else:
            missing.append('location')
        
        # Person check
        if re.search(r'मुख्यमंत्री|ओपी चौधरी|CM', answer, re.IGNORECASE):
            score += 1
        else:
            missing.append('person')
        
        # Amount/number check (if query asks for it)
        if any(k in query.lower() for k in ['कितनी', 'amount', 'राशि']):
            if re.search(r'₹|करोड़|लाख', answer):
                score += 1
            else:
                missing.append('amount')
        else:
            score += 1  # Not required
        
        return {"score": score, "missing": missing}


# Singleton instance
_fast_nlq_service = None

def get_fast_nlq_service() -> FastNLQService:
    """Get singleton instance of FastNLQService"""
    global _fast_nlq_service
    if _fast_nlq_service is None:
        _fast_nlq_service = FastNLQService()
    return _fast_nlq_service
