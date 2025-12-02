import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import update
from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent

async def reset_enrichment():
    print("🔄 Resetting enrichment data for ALL tweets...")
    async with AsyncSessionLocal() as session:
        # Reset fields to NULL
        # Note: cognitive_view and quality_flags are not in the model yet
        stmt = update(ParsedEvent).values(
            word_buckets=None
        )
        result = await session.execute(stmt)
        await session.commit()
        print(f"✅ Reset complete. {result.rowcount} tweets cleared.")

if __name__ == "__main__":
    asyncio.run(reset_enrichment())
