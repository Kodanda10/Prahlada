from typing import List, Dict, Any
from sqlalchemy import select, String
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal
from .models import ParsedEvent
from .vector_store import get_vector_store
from .cognitive.query_translator import get_query_translator

class QueryEngine:
    """
    Orchestrates Hybrid Search: SQL Filters + Vector Search.
    """
    
    def __init__(self):
        self.translator = get_query_translator()
        # Use Knowledge Base index
        self.vector_store = get_vector_store(index_path="data/knowledge_base/faiss_index.bin")
        
    async def query(self, user_query: str) -> Dict[str, Any]:
        """
        Execute a natural language query.
        """
        # 1. Translate NL -> Structured
        structured = self.translator.translate(user_query)
        vector_query = structured.get("vector_query", user_query)
        filters = structured.get("filters", {})
        limit = structured.get("limit", 10)
        
        print(f"🔍 Executing Query: '{user_query}'")
        print(f"   - Vector Term: {vector_query}")
        print(f"   - Filters: {filters}")
        
        # 2. Vector Search (Semantic)
        # Get more candidates than needed to allow for filtering
        vector_results = self.vector_store.search(vector_query, k=limit * 2)
        
        if not vector_results:
            return {"results": [], "structured_query": structured}
            
        # Extract Tweet IDs from vector results
        # Assuming metadata contains 'tweet_id'
        # If metadata doesn't have tweet_id, we might need to rely on text matching or index ID
        # For now, let's assume metadata has tweet_id or we use the text to find it
        
        # 3. SQL Search (Metadata/Filters)
        # We'll fetch full objects for the vector matches
        # And apply SQL filters if possible
        
        results = []
        async with AsyncSessionLocal() as session:
            for res in vector_results:
                meta = res['metadata']
                tweet_id = meta.get('tweet_id')
                
                if not tweet_id:
                    continue
                    
                # Build SQL Query
                stmt = select(ParsedEvent).where(ParsedEvent.tweet_id == tweet_id)
                
                # Apply Filters (Basic implementation)
                if filters.get("location"):
                    # Handle JSON array for locations
                    # Simple approach: Check if the JSON string contains the location name
                    # This works for both SQLite (JSON) and Postgres (Array cast to text)
                    loc_filter = filters["location"]
                    stmt = stmt.where(ParsedEvent.locations.cast(String).contains(loc_filter))
                    
                if filters.get("event_type"):
                    stmt = stmt.where(ParsedEvent.event_type == filters["event_type"])
                
                # Execute
                db_res = await session.execute(stmt)
                event = db_res.scalar_one_or_none()
                
                if event:
                    results.append({
                        "event": event,
                        "score": res['distance'],
                        "reasoning": meta.get('reasoning', '')
                    })
                    
                if len(results) >= limit:
                    break
                    
        return {
            "results": results,
            "structured_query": structured
        }

_query_engine = None

def get_query_engine() -> QueryEngine:
    global _query_engine
    if _query_engine is None:
        _query_engine = QueryEngine()
    return _query_engine
