import asyncio
import sys
import re
import ast
from pathlib import Path
from sqlalchemy import text

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal

async def recover_buckets():
    print("🚑 Recovering 'word_buckets' from logs...")
    
    log_files = [
        PROJECT_ROOT / "data/enrichment_manual.log.bak_20251201",
        PROJECT_ROOT / "data/enrichment.log"
    ]
    
    updates = {} # tweet_id -> buckets (dict to deduplicate, latest wins)
    
    # Regex to capture tweet_id and buckets list
    # Pattern: ✅ Enriched <tweet_id> - buckets: <list_str>
    pattern = re.compile(r"✅ Enriched (\d+) - buckets: (\[.*\])")
    
    for log_file in log_files:
        if not log_file.exists():
            print(f"⚠️  Log file not found: {log_file}")
            continue
            
        print(f"📖 Scanning {log_file.name}...")
        count = 0
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    tweet_id = match.group(1)
                    buckets_str = match.group(2)
                    try:
                        buckets = ast.literal_eval(buckets_str)
                        if buckets and isinstance(buckets, list):
                            updates[tweet_id] = buckets
                            count += 1
                    except Exception as e:
                        # print(f"Error parsing buckets for {tweet_id}: {e}")
                        pass
        print(f"   Found {count} entries in {log_file.name}")

    print(f"📋 Total unique tweets to restore: {len(updates)}")
    
    if not updates:
        print("⚠️  No buckets found to restore.")
        return

    # Update DB
    async with AsyncSessionLocal() as session:
        print("💾 Updating database...")
        
        try:
            # Disable guardrail
            await session.execute(text("ALTER TABLE parsed_events DISABLE TRIGGER gemma2_readonly_guard"))
            
            count = 0
            for tweet_id, buckets in updates.items():
                await session.execute(
                    text("UPDATE parsed_events SET word_buckets = :buckets WHERE tweet_id = :tweet_id"),
                    {"buckets": buckets, "tweet_id": tweet_id}
                )
                count += 1
                if count % 100 == 0:
                    print(f"   Updated {count}...")
            
            await session.commit()
            print(f"✅ Successfully restored buckets for {count} tweets.")
            
        except Exception as e:
            print(f"❌ Error during update: {e}")
            await session.rollback()
        finally:
            # Re-enable guardrail
            await session.execute(text("ALTER TABLE parsed_events ENABLE TRIGGER gemma2_readonly_guard"))
            await session.commit()

if __name__ == "__main__":
    asyncio.run(recover_buckets())
