"""
Event Object Loader - Load from Database
Converts EnrichedItem records into EventObject format for fast NLQ
"""

from typing import List, Dict, Any
import asyncio


async def load_events_from_db() -> List[Dict[str, Any]]:
    """
    Load all enriched items from database and convert to EventObject format.
    """
    from backend.database import AsyncSessionLocal
    from backend.models import EnrichedItem
    from sqlalchemy import select
    
    events = []
    
    async with AsyncSessionLocal() as session:
        # Fetch all enriched items with metadata
        result = await session.execute(
            select(EnrichedItem).where(EnrichedItem.metadata != None)
        )
        enriched_items = result.scalars().all()
        
        print(f"📊 Loading {len(enriched_items)} enriched items from database...")
        
        for item in enriched_items:
            try:
                # EnrichedItem fields: themes, event_type, sentiment, location_candidates, 
                # schemes, communities, people, organizations, layers, notes
                
                # Build event object
                event = {
                    "event_id": f"enriched_{item.tweet_id}",
                    "tweet_ids": [str(item.tweet_id)],
                    "scheme_name": item.schemes[0] if item.schemes and len(item.schemes) > 0 else (item.notes[:50] if item.notes else "Unknown Event"),
                    "event_type": item.event_type or 'general',
                    "event_date": None,  # TODO: Extract from RawTweet join
                    "event_time": None,
                    "event_date_display": None,
                    "location": {
                        "city": item.location_candidates.get('city') if isinstance(item.location_candidates, dict) else None,
                        "venue": item.location_candidates.get('venue') if isinstance(item.location_candidates, dict) else None,
                        "district": item.location_candidates.get('district') if isinstance(item.location_candidates, dict) else None,
                        "assembly_constituency": None,
                        "state": "छत्तीसगढ़"
                    },
                    "leaders_main": item.people[:1] if item.people and len(item.people) > 0 else [],
                    "leaders_others": item.people[1:] if item.people and len(item.people) > 1 else [],
                    "announcements": {
                        "amount": None,  # TODO: Extract from notes or layers
                        "employment": None,
                        "beneficiaries": None
                    },
                    "objectives": [],
                    "facilities": [],
                    "milestones": [],
                    "narrative": {
                        "tags": item.themes if item.themes else [],
                        "political_context": item.notes,
                        "quotes": []
                    },
                    "confidence": item.confidence_score or 0.7,
                    "keywords_hindi": item.themes if item.themes else [],
                    "keywords_english": []
                }
                
                events.append(event)
                
            except Exception as e:
                print(f"⚠️ Error processing item {item.tweet_id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"✅ Successfully loaded {len(events)} events")
        
    return events


def get_all_events_sync() -> List[Dict[str, Any]]:
    """
    Synchronous wrapper to load events from database.
    """
    # Import the hardcoded critical events
    from backend.cognitive.event_objects import CRITICAL_EVENTS
    
    # Try to load from database
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If event loop is already running, create a new one
            import nest_asyncio
            nest_asyncio.apply()
            db_events = loop.run_until_complete(load_events_from_db())
        else:
            db_events = asyncio.run(load_events_from_db())
        
        # Combine critical events (high quality) with DB events
        all_events = CRITICAL_EVENTS + db_events
        print(f"📦 Total events: {len(CRITICAL_EVENTS)} critical + {len(db_events)} from DB = {len(all_events)}")
        
        return all_events
        
    except Exception as e:
        print(f"⚠️ Failed to load from database: {e}")
        print("   Falling back to critical events only")
        return CRITICAL_EVENTS
