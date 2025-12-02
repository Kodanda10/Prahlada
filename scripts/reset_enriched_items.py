import asyncio
from backend.database import engine
from backend.models import Base, EnrichedItem

async def reset_table():
    async with engine.begin() as conn:
        print("Dropping enriched_items table...")
        await conn.run_sync(lambda sync_conn: EnrichedItem.__table__.drop(sync_conn, checkfirst=True))
        print("Recreating tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(reset_table())
