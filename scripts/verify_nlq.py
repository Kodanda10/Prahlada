import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.query_engine import get_query_engine
from backend.cognitive.phi_adapter import set_phi_adapter_config

async def verify_nlq():
    print("💬 Verifying Natural Language Query (V6.0)...")
    
    # 1. Enable Phi Adapter (Mocked for speed/determinism)
    set_phi_adapter_config(enabled=True)
    
    engine = get_query_engine()
    
    # Mock Translator to avoid actual LLM call for this test
    # We want to verify the Engine logic, not the LLM's stochasticity
    engine.translator.translate = MagicMock(return_value={
        "vector_query": "textile park",
        "filters": {"location": "Raipur"},
        "limit": 5
    })
    print("✅ Mocked Query Translator")
    
    # Debug: Print all events to check data
    from backend.database import AsyncSessionLocal
    from backend.models import ParsedEvent
    from sqlalchemy import select
    
    print("\n🔍 Debug: Checking DB Content...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ParsedEvent))
        events = result.scalars().all()
        for e in events:
            meta = e.gemini_metadata or {}
            print(f"   - ID: {e.tweet_id} | Locations: {e.locations} | Text: {meta.get('original_text', '')[:30]}...")

    # 2. Execute Query
    query = "Show me textile park events in Raipur"
    print(f"\n❓ User Query: '{query}'")
    
    response = await engine.query(query)
    
    # 3. Verify Results
    results = response["results"]
    print(f"\n🔎 Found {len(results)} results:")
    
    for i, res in enumerate(results):
        event = res['event']
        print(f"   {i+1}. [{event.event_type}] {event.raw_text[:80]}...")
        print(f"      Location: {event.location}")
        print(f"      Score: {res['score']:.4f}")
        
    if len(results) > 0:
        print("\n✅ NLQ Verification Successful!")
    else:
        print("\n⚠️ No results found. Check if data exists and filters match.")

if __name__ == "__main__":
    asyncio.run(verify_nlq())
