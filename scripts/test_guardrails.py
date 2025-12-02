import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal

async def test_guardrails():
    print("🧪 Testing database guardrails...")
    async with AsyncSessionLocal() as session:
        try:
            # Attempt to delete from parsed_events
            print("   Attempting to DELETE from parsed_events...")
            await session.execute(text("DELETE FROM parsed_events WHERE tweet_id = 'test_id'"))
            await session.commit()
            print("❌ Guardrail FAILED! Deletion was allowed.")
        except Exception as e:
            if "ACCESS DENIED" in str(e):
                print("✅ Guardrail PASSED! Deletion blocked with message:")
                print(f"   {str(e).split('CONTEXT:')[0].strip()}")
            else:
                print(f"⚠️  Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_guardrails())
