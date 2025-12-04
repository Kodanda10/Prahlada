"""
Database migration to add Review Arbitration columns.

Run this after stopping the backend server:
python backend/migrations/add_review_arbitration_columns.py
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from backend.database import engine


async def run_migration():
    """Add review arbitration columns to parsed_events table."""
    
    print("Starting migration: Add Review Arbitration Columns")
    print("=" * 60)
    
    async with engine.begin() as conn:
        # Check if columns already exist
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'parsed_events' 
            AND column_name IN ('final_data', 'feedback_log', 'cognitive_view')
        """)
        
        result = await conn.execute(check_query)
        existing_columns = [row[0] for row in result]
        
        if len(existing_columns) == 3:
            print("✅ All columns already exist. Migration not needed.")
            return
        
        print(f"Found {len(existing_columns)} existing columns. Adding missing columns...")
        
        # Add final_data column
        if 'final_data' not in existing_columns:
            print("Adding column: final_data")
            await conn.execute(text("""
                ALTER TABLE parsed_events 
                ADD COLUMN IF NOT EXISTS final_data JSONB
            """))
            print("✅ Added: final_data")
        
        # Add feedback_log column
        if 'feedback_log' not in existing_columns:
            print("Adding column: feedback_log")
            await conn.execute(text("""
                ALTER TABLE parsed_events 
                ADD COLUMN IF NOT EXISTS feedback_log JSONB
            """))
            print("✅ Added: feedback_log")
        
        # Add cognitive_view column
        if 'cognitive_view' not in existing_columns:
            print("Adding column: cognitive_view")
            await conn.execute(text("""
                ALTER TABLE parsed_events 
                ADD COLUMN IF NOT EXISTS cognitive_view JSONB
            """))
            print("✅ Added: cognitive_view")
        
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("\nYou can now restart the backend server.")


if __name__ == "__main__":
    asyncio.run(run_migration())
