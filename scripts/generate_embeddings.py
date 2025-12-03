import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy import select

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal
from backend.models import EnrichedItem
from backend.vector_store import get_vector_store

async def generate_embeddings():
    print("🚀 Starting Embedding Generation for Enriched Items...")
    
    # 0. Clean existing index to avoid duplication/corruption
    vector_store = get_vector_store()
    if os.path.exists(vector_store.index_path):
        os.remove(vector_store.index_path)
    if os.path.exists(vector_store.metadata_path):
        os.remove(vector_store.metadata_path)
        
    # Re-initialize to get clean state
    vector_store.index = None
    vector_store.metadata = []
    
    # 1. Initialize Vector Store (already got instance, just ensured clean)
    
    # 2. Fetch Enriched Items
    async with AsyncSessionLocal() as session:
        query = select(EnrichedItem)
        result = await session.execute(query)
        items = result.scalars().all()
    
    print(f"📊 Found {len(items)} enriched items.")
    
    if not items:
        print("⚠️ No enriched items found. Run enrichment first.")
        return

    # 3. Prepare Documents
    documents = []
    for item in items:
        # Construct semantic text representation
        # Format: "Event: <type>. Themes: <themes>. Text: <notes/summary>"
        
        themes_str = ", ".join(item.themes) if item.themes else ""
        schemes_str = ", ".join(item.schemes) if item.schemes else ""
        
        # Use notes if available, otherwise fallback to themes/event
        content_text = item.notes or ""
        
        semantic_text = f"Event: {item.event_type}. Themes: {themes_str}. Schemes: {schemes_str}. Content: {content_text}"
        
        doc = {
            "tweet_id": item.tweet_id,
            "text": semantic_text,
            "metadata": {
                "event_type": item.event_type,
                "themes": item.themes,
                "schemes": item.schemes,
                "sentiment": item.sentiment
            }
        }
        documents.append(doc)
    
    # 4. Batch Upsert to Vector Store
    # VectorStore.add_documents expects list[dict] with 'text' key.
    # It stores the whole dict as metadata.
    
    print(f"embedding {len(documents)} documents...")
    vector_store.add_documents(documents)
    
    # 5. Save Index
    vector_store.save()
    print("✅ Embeddings generated and saved.")

if __name__ == "__main__":
    asyncio.run(generate_embeddings())
