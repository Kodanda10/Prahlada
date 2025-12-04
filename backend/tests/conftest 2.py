"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import AdminUser, RawTweet, ParsedEvent


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for tests."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def async_db_session(async_engine):
    """Create async database session for tests."""
    async_session = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_raw_tweet():
    """Sample RawTweet for testing."""
    from datetime import datetime
    return RawTweet(
        tweet_id="sample123",
        text="Sample tweet content in Hindi: मुख्यमंत्री ने दौरा किया",
        created_at=datetime.utcnow(),
        author_handle="@cggovt",
        processing_status="processed",
    )


@pytest.fixture
def sample_parsed_event():
    """Sample ParsedEvent for testing."""
    import uuid
    return ParsedEvent(
        id=str(uuid.uuid4()),
        tweet_id="parsed123",
        event_type="दौरा",
        locations=["रायपुर"],
        people_mentioned=["मुख्यमंत्री"],
        overall_confidence=0.85,
        needs_review=False,
        review_status="approved",
    )


@pytest.fixture
def sample_admin_user():
    """Sample AdminUser for testing."""
    return AdminUser(
        username="testadmin",
        password_hash="$2b$12$fake_hash_for_testing",
        roles=["admin"],
        display_name="Test Administrator",
        is_active=True,
    )
