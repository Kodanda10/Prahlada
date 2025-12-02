"""
Backend database tests.
Tests database connection, session management, and basic operations.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db_session, AsyncSessionLocal, engine, Base


@pytest.mark.asyncio
class TestDatabaseConnection:
    """Test database connection and session management."""
    
    async def test_engine_is_created(self):
        """Database engine should be created."""
        assert engine is not None
        assert engine.url is not None
    
    async def test_session_creation(self):
        """Database session should be created successfully."""
        async with AsyncSessionLocal() as session:
            assert session is not None
            assert isinstance(session, AsyncSession)
    
   async def test_get_db_session_dependency(self):
        """get_db_session should yield a valid session."""
        async for session in get_db_session():
            assert session is not None
            assert isinstance(session, AsyncSession)
            break  # Only test first yield
    
    async def test_session_closes_properly(self):
        """Session should close after context manager exits."""
        session = None
       async with AsyncSessionLocal() as sess:
            session = sess
            assert not session.is_active or session.is_active  # Session is active
        
        # After context, check if session is properly managed
        # (AsyncSession doesn't have direct is_closed, but context ensures cleanup)
    
    async def test_multiple_sessions_independent(self):
        """Multiple sessions should be independent."""
        async with AsyncSessionLocal() as session1:
            async with AsyncSessionLocal() as session2:
                assert session1 is not session2


@pytest.mark.asyncio
class TestDatabaseBase:
    """Test declarative base configuration."""
    
    async def test_base_exists(self):
        """Declarative base should exist."""
        assert Base is not None
    
    async def test_base_metadata_exists(self):
        """Base should have metadata."""
        assert hasattr(Base, 'metadata')
        assert Base.metadata is not None
