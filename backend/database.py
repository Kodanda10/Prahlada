import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from a .env file
load_dotenv()

# --- Database Connection Setup ---
# It's crucial that your DATABASE_URL is set in your environment or a .env file.
# Format for asyncpg: "postgresql+asyncpg://user:password@host:port/dbname"
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please create a .env file or set it.")

# --- SQLAlchemy Engine and Session ---
# Create an asynchronous engine for FastAPI to use.
# `echo=False` in production to avoid logging every SQL query.
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Create a sessionmaker that will be used to create new sessions for each request.
# `expire_on_commit=False` is important for async sessions.
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Declarative Base ---
# All of our ORM models will inherit from this Base.
Base = declarative_base()

# --- Dependency for FastAPI ---
# This function will be used as a dependency in our API routes to get a database session.
async def get_db_session() -> AsyncSession:
    """
    Dependency function that yields a new SQLAlchemy AsyncSession for each request.
    """
    async with AsyncSessionLocal() as session:
        yield session

# --- Guardrails Integration ---
from sqlalchemy import event
from sqlalchemy.orm import Session
from .security.guardrail import Guardrail

@event.listens_for(Session, "before_delete")
def prevent_critical_deletes(session, instances):
    for instance in instances:
        table_name = instance.__tablename__
        # Check if deletion is allowed
        if not Guardrail.validate_delete(table_name):
            raise ValueError(f"Deletion blocked by Guardrail for table: {table_name}")
            
# Note: For AsyncSession, events are a bit complex, but Session events often propagate.
# If this doesn't work, we might need to hook into the underlying sync session or engine.
