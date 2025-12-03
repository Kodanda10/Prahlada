import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import AsyncSessionLocal

async def add_guardrails():
    """
    Adds a PostgreSQL trigger to prevent DELETE or UPDATE on the parsed_events table.
    """
    print("🛡️  Adding guardrails to 'parsed_events' table...")
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Create the trigger function
            create_func_sql = """
            CREATE OR REPLACE FUNCTION prevent_gemma2_deletion()
            RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION '🚫 ACCESS DENIED: Gemma 2 enrichment data (parsed_events) is READ-ONLY. Modification or deletion is strictly prohibited.';
            END;
            $$ LANGUAGE plpgsql;
            """
            await session.execute(text(create_func_sql))
            print("✅ Trigger function created.")
            
            # 2. Create the trigger for parsed_events (Gemma 2 - READ ONLY)
            drop_trigger_sql = "DROP TRIGGER IF EXISTS gemma2_readonly_guard ON parsed_events;"
            await session.execute(text(drop_trigger_sql))
            
            create_trigger_sql = """
            CREATE TRIGGER gemma2_readonly_guard
            BEFORE DELETE OR UPDATE ON parsed_events
            FOR EACH ROW
            EXECUTE FUNCTION prevent_gemma2_deletion();
            """
            await session.execute(text(create_trigger_sql))
            print("✅ Trigger 'gemma2_readonly_guard' applied to 'parsed_events'.")
            
            # 3. Create the trigger function for enriched_items (Gemma 3 - NO DELETE)
            create_func_g3_sql = """
            CREATE OR REPLACE FUNCTION prevent_gemma3_deletion()
            RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION '🚫 ACCESS DENIED: Gemma 3 enrichment data (enriched_items) is protected from DELETION.';
            END;
            $$ LANGUAGE plpgsql;
            """
            await session.execute(text(create_func_g3_sql))
            
            # 4. Create the trigger for enriched_items
            drop_trigger_g3_sql = "DROP TRIGGER IF EXISTS gemma3_deletion_guard ON enriched_items;"
            await session.execute(text(drop_trigger_g3_sql))
            
            create_trigger_g3_sql = """
            CREATE TRIGGER gemma3_deletion_guard
            BEFORE DELETE ON enriched_items
            FOR EACH ROW
            EXECUTE FUNCTION prevent_gemma3_deletion();
            """
            await session.execute(text(create_trigger_g3_sql))
            print("✅ Trigger 'gemma3_deletion_guard' applied to 'enriched_items'.")
            
            await session.commit()
            print("\n🔒 Guardrails active!")
            print("   - 'parsed_events': READ-ONLY (No DELETE/UPDATE)")
            print("   - 'enriched_items': PROTECTED (No DELETE, Update allowed)")
            
        except Exception as e:
            print(f"❌ Failed to add guardrails: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(add_guardrails())
