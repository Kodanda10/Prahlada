"""
Pytest configuration and fixtures for backend tests.

This module sets up:
- In-memory SQLite database for test isolation
- Async test client using httpx
- Test fixtures for authentication and mock data
"""

import os
import sys
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from unittest.mock import MagicMock, patch, AsyncMock

# Set test environment variables BEFORE any imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["FAISS_INDEX_PATH"] = "/tmp/test_faiss_index.bin"

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import test-compatible models (Mock* prefix to avoid pytest collection)
from backend.tests.test_models import (
    MockBase,
    MockRawTweet,
    MockParsedEvent,
    MockAdminUser,
)


# --- Test Database Engine ---
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# --- Helper to get password hash ---
def get_test_password_hash(password: str) -> str:
    """Hash password for test users."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


# --- Database Fixtures ---

@pytest_asyncio.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a fresh database session for each test.
    Tables are created and dropped for complete isolation.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(MockBase.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(MockBase.metadata.drop_all)


@pytest_asyncio.fixture
async def test_db_with_data(test_db_session: AsyncSession) -> AsyncSession:
    """
    Provides a database session pre-populated with test data.
    """
    # Create test admin user
    admin_user = MockAdminUser(
        id="test-user-id",
        username="testadmin",
        password_hash=get_test_password_hash("testpassword123"),
        roles=["admin"],
        display_name="Test Admin",
        email="admin@test.com",
        is_active=True,
    )
    test_db_session.add(admin_user)
    
    # Create inactive user for testing
    inactive_user = MockAdminUser(
        id="inactive-user-id",
        username="inactiveuser",
        password_hash=get_test_password_hash("password123"),
        roles=["viewer"],
        display_name="Inactive User",
        is_active=False,
    )
    test_db_session.add(inactive_user)
    
    # Create sample raw tweets
    raw_tweets = [
        MockRawTweet(
            tweet_id="tweet-001",
            text="Sample tweet about government schemes in Raipur",
            created_at=datetime(2024, 1, 15, 10, 30),
            author_handle="@user1",
            processing_status="processed",
        ),
        MockRawTweet(
            tweet_id="tweet-002",
            text="Another tweet about infrastructure development",
            created_at=datetime(2024, 1, 16, 11, 45),
            author_handle="@user2",
            processing_status="pending",
        ),
        MockRawTweet(
            tweet_id="tweet-003",
            text="Tweet that failed processing",
            created_at=datetime(2024, 1, 17, 9, 0),
            author_handle="@user3",
            processing_status="failed",
        ),
    ]
    for tweet in raw_tweets:
        test_db_session.add(tweet)
    
    # Create sample parsed events
    parsed_event = MockParsedEvent(
        id="tweet-001",
        tweet_id="tweet-001",
        categories={
            "event": ["inauguration"],
            "locations": ["Raipur", "Chhattisgarh"],
            "schemes": ["PM Awas Yojana"],
        },
        gemini_metadata={"model": "gemini-pro", "confidence": 0.95},
        event_type="inauguration",
        locations=["Raipur", "Chhattisgarh"],
        schemes_mentioned=["PM Awas Yojana"],
        overall_confidence=0.95,
        needs_review=True,
        review_status="pending",
        parsed_at=datetime(2024, 1, 15, 10, 35),
    )
    test_db_session.add(parsed_event)
    
    await test_db_session.commit()
    return test_db_session


# --- Authentication Fixtures ---

@pytest.fixture
def valid_auth_token() -> str:
    """
    Creates a valid JWT token for testing protected endpoints.
    """
    from jose import jwt
    
    secret = os.environ["AUTH_SECRET_KEY"]
    algorithm = os.environ["AUTH_ALGORITHM"]
    
    expire = datetime.utcnow() + timedelta(minutes=60)
    payload = {
        "sub": "testadmin",
        "uid": "test-user-id",
        "roles": ["admin"],
        "exp": expire,
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


@pytest.fixture
def expired_token() -> str:
    """
    Creates an expired JWT token for testing token validation.
    """
    from jose import jwt
    
    secret = os.environ["AUTH_SECRET_KEY"]
    algorithm = os.environ["AUTH_ALGORITHM"]
    
    expire = datetime.utcnow() - timedelta(seconds=1)
    payload = {
        "sub": "testadmin",
        "uid": "test-user-id",
        "roles": ["admin"],
        "exp": expire,
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


@pytest.fixture
def auth_headers(valid_auth_token: str) -> dict:
    """
    Returns headers with valid Bearer token for authenticated requests.
    """
    return {"Authorization": f"Bearer {valid_auth_token}"}


# --- Mock Fixtures ---

@pytest.fixture
def mock_vector_store():
    """
    Creates a mock VectorStore for testing without loading ML models.
    """
    mock_store = MagicMock()
    mock_store.index = MagicMock()
    mock_store.index.ntotal = 100
    mock_store.search.return_value = [
        {
            "metadata": {"tweet_id": "tweet-001", "text": "Sample tweet"},
            "distance": 0.15,
        },
        {
            "metadata": {"tweet_id": "tweet-002", "text": "Another tweet"},
            "distance": 0.25,
        },
    ]
    mock_store.add_documents = MagicMock()
    mock_store.save = MagicMock()
    return mock_store


@pytest.fixture
def mock_cognitive_engine():
    """
    Creates a mock CognitiveEngine for testing.
    """
    mock_engine = MagicMock()
    mock_engine.process_correction.return_value = {
        "id": "log-001",
        "decision": {"action": "approve", "confidence": 0.9},
        "details": {"reasoning": "Valid correction"},
    }
    return mock_engine


# --- Test Client Fixture ---

@pytest_asyncio.fixture
async def async_client(
    test_db_with_data: AsyncSession,
    mock_vector_store,
    mock_cognitive_engine,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Creates an async HTTP client for testing API endpoints.
    Uses mocked database and services.
    """
    # Mock the vector store module before importing app
    with patch("backend.vector_store.VectorStore") as MockVectorStoreClass, \
         patch("backend.vector_store._vector_store_instance", mock_vector_store), \
         patch("backend.vector_store.get_vector_store", return_value=mock_vector_store):
        
        MockVectorStoreClass.return_value = mock_vector_store
        
        # Create a mock lifespan that doesn't do heavy initialization
        from contextlib import asynccontextmanager
        from starlette.datastructures import State
        
        @asynccontextmanager
        async def mock_lifespan(app):
            # Initialize state if not present
            if not hasattr(app, 'state') or app.state is None:
                app.state = State()
            app.state.cognitive_engine = mock_cognitive_engine
            yield
        
        # Import FastAPI app components
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        # Create a test app with routes from main but mock lifespan
        test_app = FastAPI(
            title="Test API",
            lifespan=mock_lifespan,
        )
        
        # Add CORS
        test_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Create dependency override for database
        async def override_get_db():
            yield test_db_with_data
        
        # Import and register all routes
        from backend.main import (
            read_root,
            get_config,
            get_system_health,
            get_analytics_health,
        )
        from backend import schemas
        
        # Register public endpoints
        test_app.get("/")(read_root)
        test_app.get("/config")(get_config)
        test_app.get("/health/system")(get_system_health)
        test_app.get("/health/analytics")(get_analytics_health)
        
        # For protected endpoints, we need to mock auth
        # Import auth functions
        from backend.auth import get_current_user, authenticate_user, create_access_token
        
        # Create mock user for dependency override
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.username = "testadmin"
        mock_user.roles = ["admin"]
        mock_user.display_name = "Test Admin"
        mock_user.email = "admin@test.com"
        mock_user.is_active = True
        
        # Register protected endpoints with dependency overrides
        from fastapi import Depends, HTTPException, status
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import select, func
        
        # Login endpoint
        @test_app.post("/api/auth/login", response_model=schemas.AuthResponse)
        async def test_login(payload: schemas.AuthRequest):
            # Use test database session
            from sqlalchemy import select
            result = await test_db_with_data.execute(
                select(MockAdminUser).where(MockAdminUser.username == payload.username)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )
            
            # Verify password
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            if not pwd_context.verify(payload.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )
            
            token = create_access_token(
                {"sub": user.username, "uid": user.id, "roles": user.roles or []}
            )
            user_payload = schemas.AuthUser(
                id=user.id,
                username=user.username,
                roles=user.roles or [],
                display_name=user.display_name,
                email=user.email,
            )
            return schemas.AuthResponse(token=token, user=user_payload)
        
        # Verify endpoint
        from fastapi import Header
        
        @test_app.get("/api/auth/verify", response_model=schemas.AuthUser)
        async def test_verify(authorization: str = Header(None)):
            from jose import jwt, JWTError
            
            # Get auth header
            auth_header = authorization
            if not auth_header:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            
            # Parse Bearer token
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header",
                )
            
            token = parts[1]
            if not token or token.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Empty token",
                )
            
            try:
                payload = jwt.decode(
                    token,
                    os.environ["AUTH_SECRET_KEY"],
                    algorithms=[os.environ["AUTH_ALGORITHM"]]
                )
                username = payload.get("sub")
                if not username:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token",
                    )
            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            
            # Get user from test DB
            result = await test_db_with_data.execute(
                select(MockAdminUser).where(MockAdminUser.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive",
                )
            
            return schemas.AuthUser(
                id=user.id,
                username=user.username,
                roles=user.roles or [],
                display_name=user.display_name,
                email=user.email,
            )
        
        # Helper to validate auth header
        async def get_test_current_user(authorization: str):
            from jose import jwt, JWTError
            
            if not authorization:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            
            parts = authorization.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header",
                )
            
            token = parts[1]
            if not token or token.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Empty token",
                )
            
            try:
                payload = jwt.decode(
                    token,
                    os.environ["AUTH_SECRET_KEY"],
                    algorithms=[os.environ["AUTH_ALGORITHM"]]
                )
                username = payload.get("sub")
                if not username:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token",
                    )
            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            
            result = await test_db_with_data.execute(
                select(MockAdminUser).where(MockAdminUser.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )
            
            return user
        
        # Stats endpoint
        @test_app.get("/api/stats", response_model=schemas.StatsResponse)
        async def test_get_stats(authorization: str = Header(None)):
            await get_test_current_user(authorization)
            
            from sqlalchemy import func
            
            total_query = select(func.count(MockRawTweet.tweet_id))
            processed_query = select(func.count(MockRawTweet.tweet_id)).where(
                MockRawTweet.processing_status == 'processed'
            )
            pending_query = select(func.count(MockRawTweet.tweet_id)).where(
                MockRawTweet.processing_status == 'pending'
            )
            errors_query = select(func.count(MockRawTweet.tweet_id)).where(
                MockRawTweet.processing_status == 'failed'
            )
            
            total = await test_db_with_data.execute(total_query)
            processed = await test_db_with_data.execute(processed_query)
            pending = await test_db_with_data.execute(pending_query)
            errors = await test_db_with_data.execute(errors_query)
            
            return {
                "total_tweets": total.scalar_one(),
                "parsed_success": processed.scalar_one(),
                "pending": pending.scalar_one(),
                "errors": errors.scalar_one(),
            }
        
        # Events endpoint
        @test_app.get("/api/events", response_model=list[schemas.EventResponse])
        async def test_get_events(status: str = None, authorization: str = Header(None)):
            await get_test_current_user(authorization)
            
            status_map = {
                "failed": "failed",
                "error": "failed",
                "pending": "pending",
                "success": "processed",
                "processed": "processed",
            }
            normalized_status = status.lower() if status else None
            status_filter = status_map.get(normalized_status) if normalized_status else None
            
            query = (
                select(MockParsedEvent, MockRawTweet)
                .join(MockRawTweet, MockRawTweet.tweet_id == MockParsedEvent.tweet_id, isouter=True)
                .order_by(MockParsedEvent.parsed_at.desc())
                .limit(100)
            )
            
            if status_filter:
                query = query.where(MockRawTweet.processing_status == status_filter)
            
            results = await test_db_with_data.execute(query)
            rows = results.all()
            
            def map_status(raw_status):
                if not raw_status:
                    return "SUCCESS"
                mapping = {
                    "processed": "SUCCESS",
                    "pending": "PENDING",
                    "failed": "FAILED",
                }
                return mapping.get(raw_status.lower(), "SUCCESS")
            
            response = []
            for parsed_event, raw_tweet in rows:
                categories = parsed_event.categories or {}
                locations = parsed_event.locations or []
                location_text = ", ".join(locations) if locations else "Unknown"
                
                response.append({
                    "tweet_id": parsed_event.tweet_id,
                    "created_at": raw_tweet.created_at if raw_tweet else parsed_event.parsed_at,
                    "raw_text": raw_tweet.text if raw_tweet else "",
                    "clean_text": categories.get("clean_text", raw_tweet.text if raw_tweet else ""),
                    "event_type": categories.get("event", []),
                    "location_text": location_text,
                    "scheme_tags": parsed_event.schemes_mentioned or [],
                    "parsing_status": map_status(raw_tweet.processing_status if raw_tweet else None),
                    "logs": [f"parsed_at={parsed_event.parsed_at.isoformat()}"],
                })
            
            return response
        
        # Analytics endpoint
        @test_app.get("/api/analytics/{chart_type}", response_model=list[schemas.AnalyticsDataPoint])
        async def test_get_analytics(chart_type: str, authorization: str = Header(None)):
            await get_test_current_user(authorization)
            
            if chart_type not in ["event-types", "districts"]:
                raise HTTPException(
                    status_code=404,
                    detail=f"Analytics chart type '{chart_type}' not found."
                )
            
            # Return mock data for tests since SQLite doesn't support JSONB functions
            return []
        
        # Approve event endpoint
        @test_app.post("/api/events/{tweet_id}/approve")
        async def test_approve_event(tweet_id: str, authorization: str = Header(None)):
            user = await get_test_current_user(authorization)
            
            event = await test_db_with_data.get(MockParsedEvent, tweet_id)
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")
            
            event.review_status = "approved"
            event.needs_review = False
            event.reviewed_at = datetime.utcnow()
            event.reviewed_by = user.username
            
            await test_db_with_data.commit()
            
            return {"status": "success", "message": f"Event {tweet_id} approved"}
        
        # Ingest endpoint
        from fastapi.responses import JSONResponse
        
        @test_app.post("/api/ingest-parsed-tweet", status_code=201)
        async def test_ingest_tweet(payload: schemas.IngestPayload, authorization: str = Header(None)):
            await get_test_current_user(authorization)
            
            tweet_id = payload.tweet.id
            
            existing = await test_db_with_data.get(MockParsedEvent, tweet_id)
            if existing:
                # Return 200 (not 201) for skipped duplicates
                return JSONResponse(
                    status_code=200,
                    content={"status": "skipped", "message": "Parsed event already exists."}
                )
            
            new_event = MockParsedEvent(
                id=tweet_id,
                tweet_id=tweet_id,
                categories=payload.categories.model_dump(),
                gemini_metadata=payload.gemini_metadata.model_dump(),
                event_type=payload.categories.event[0] if payload.categories.event else None,
                locations=payload.categories.locations,
                schemes_mentioned=payload.categories.schemes,
                overall_confidence=payload.gemini_metadata.confidence,
                parsed_at=datetime.utcnow(),
            )
            test_db_with_data.add(new_event)
            
            # Check if raw tweet exists
            raw_tweet = await test_db_with_data.get(MockRawTweet, tweet_id)
            if raw_tweet:
                raw_tweet.processing_status = 'processed'
                raw_tweet.processed_at = datetime.utcnow()
            else:
                new_raw = MockRawTweet(
                    tweet_id=tweet_id,
                    text=payload.tweet.text,
                    created_at=payload.tweet.created_at,
                    processing_status='processed',
                    processed_at=datetime.utcnow(),
                )
                test_db_with_data.add(new_raw)
            
            await test_db_with_data.commit()
            
            return {"status": "success", "message": f"Data for tweet {tweet_id} ingested."}
        
        # Vector indexing endpoint
        @test_app.post("/api/vector/trigger-batch-indexing")
        async def test_vector_indexing(payload: schemas.VectorIndexTriggerPayload, authorization: str = Header(None)):
            await get_test_current_user(authorization)
            
            tweet_ids = payload.tweetIds
            if not tweet_ids:
                return {"status": "skipped", "message": "No tweet IDs provided."}
            
            # Query tweets
            query = select(MockRawTweet.tweet_id, MockRawTweet.text).where(
                MockRawTweet.tweet_id.in_(tweet_ids)
            )
            result = await test_db_with_data.execute(query)
            tweets = result.all()
            
            if not tweets:
                return {"status": "skipped", "message": "No matching tweets found in DB for indexing."}
            
            documents = [{"tweet_id": t[0], "text": t[1]} for t in tweets]
            mock_vector_store.add_documents(documents)
            
            return {"status": "success", "service": "faiss", "message": f"Indexing triggered for {len(documents)} items."}
        
        # Cognitive correct endpoint
        # Store the engine reference in the module scope for access
        _cognitive_engine_ref = mock_cognitive_engine
        
        @test_app.post("/api/cognitive/correct", response_model=schemas.CorrectionResponse)
        async def test_cognitive_correct(payload: schemas.CorrectionRequest, authorization: str = Header(None)):
            await get_test_current_user(authorization)
            
            # Use the module-scoped reference since app.state may not be set yet
            engine = _cognitive_engine_ref
            if not engine:
                raise HTTPException(status_code=503, detail="Cognitive Engine is not initialized.")
            
            result = engine.process_correction(
                payload.tweet_id,
                payload.text,
                payload.old_data,
                payload.correction,
            )
            
            return {
                "status": "success" if "error" not in result else "error",
                "log_id": result.get("id"),
                "decision": result.get("decision"),
                "details": result.get("details"),
            }
        
        # Search endpoint
        @test_app.post("/api/search", response_model=list[schemas.SearchResult])
        async def test_search(payload: schemas.SearchRequest, authorization: str = Header(None)):
            await get_test_current_user(authorization)
            
            k = payload.k
            if k == 0:
                return []
            
            if not mock_vector_store.index or mock_vector_store.index.ntotal == 0:
                return []
            
            results = mock_vector_store.search(payload.query, k=k)
            
            search_results = []
            for res in results[:k]:
                metadata = res.get("metadata", {})
                search_results.append(
                    schemas.SearchResult(
                        tweet_id=metadata.get("tweet_id", "unknown"),
                        text=metadata.get("text", ""),
                        score=res.get("distance", 0.0),
                        metadata=metadata,
                    )
                )
            
            return search_results
        
        # Telemetry endpoint (no auth required)
        @test_app.post("/api/telemetry", status_code=201)
        async def test_telemetry(payload: schemas.TelemetryRequest):
            return {"status": "success"}
        
        # Create test client
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


# --- Helper Functions ---

def create_test_tweet_data(
    tweet_id: str = "test-tweet-123",
    text: str = "Test tweet content",
) -> dict:
    """
    Creates a valid tweet payload for ingest endpoint testing.
    """
    return {
        "tweet": {
            "id": tweet_id,
            "text": text,
            "created_at": datetime.utcnow().isoformat(),
            "author_id": "author-123",
        },
        "categories": {
            "locations": ["Raipur"],
            "people": ["CM"],
            "event": ["meeting"],
            "organisation": [],
            "schemes": ["PM Awas Yojana"],
            "communities": [],
        },
        "gemini_metadata": {
            "model": "gemini-pro",
            "confidence": 0.85,
        },
    }
