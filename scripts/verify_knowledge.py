import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy import select, func

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent, WordBucket
from backend.vector_store import get_vector_store

async def verify():
    print("🔍 Verifying Knowledge Persistence...")
    
    async with AsyncSessionLocal() as session:
        # 1. Check Word Buckets
        result = await session.execute(select(func.count(WordBucket.id)))
        bucket_count = result.scalar()
        print(f"✅ Word Buckets in DB: {bucket_count}")
        
        # 2. Check Parsed Events with Cognitive View
        result = await session.execute(select(ParsedEvent).where(ParsedEvent.cognitive_view.isnot(None)).limit(1))
        event = result.scalar_one_or_none()
        if event:
            print(f"✅ Found Parsed Event: {event.id}")
            print(f"   - Word Buckets: {event.word_buckets}")
            print(f"   - Cognitive View: {event.cognitive_view.keys() if event.cognitive_view else 'None'}")
        
        result = await session.execute(select(func.count(ParsedEvent.id)).where(ParsedEvent.cognitive_view.isnot(None)))
        event_count = result.scalar()
        print(f"✅ Parsed Events with Cognitive View: {event_count}")
        
        # 3. Check Vector Store
        vector_store = get_vector_store(index_path="data/knowledge_base/faiss_index.bin")
        print(f"✅ Vectors in FAISS Index: {vector_store.index.ntotal}")
        
        # 4. Simple Search Test
        print("\n🧪 Testing Semantic Search...")
        results = vector_store.search("textile park", k=2)
        for r in results:
            meta = r['metadata']
            print(f"   - Match (Dist: {r['distance']:.4f}): {meta.get('text')[:100]}...")

if __name__ == "__main__":
    asyncio.run(verify())
