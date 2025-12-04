import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.main import app
from backend.models import ParsedEvent, RawTweet, AdminUser
from backend.auth import get_password_hash
import datetime

@pytest.fixture
async def test_db(async_session: AsyncSession):
    """Provide a test database session."""
    return async_session

@pytest.fixture
async def test_user(test_db: AsyncSession):
    """Create a test admin user."""
    user = AdminUser(
        id="test-user-id",
        username="testuser",
        password_hash=get_password_hash("testpass"),
        roles=["admin"],
        display_name="Test User"
    )
    test_db.add(user)
    await test_db.commit()
    return user

@pytest.fixture
async def test_token(test_user):
    """Get auth token for test user."""
    from backend.auth import create_access_token
    token = create_access_token({"sub": test_user.username, "uid": test_user.id, "roles": test_user.roles})
    return token

@pytest.fixture
async def test_parsed_event(test_db: AsyncSession):
    """Create a test parsed event with parser and LLM data."""
    raw_tweet = RawTweet(
        tweet_id="test-tweet-123",
        text="CM announced new irrigation scheme for farmers in Raipur district",
        created_at=datetime.datetime.utcnow(),
        author_handle="@test_handle",
        processing_status="processed"
    )
    test_db.add(raw_tweet)
    
    parsed_event = ParsedEvent(
        id="test-event-123",
        tweet_id="test-tweet-123",
        categories={
            "event_type": "Meeting",
            "people": ["CM Baghel"],
            "schemes": ["Irrigation Scheme"],
            "communities": ["Farmers"],
            "location": {"district": "Raipur"}
        },
        gemini_metadata={"model": "gemini-1.5", "confidence": 0.85},
        event_type="Policy Announcement",  # LLM says different
        people_mentioned=["Bhupesh Baghel"],  # LLM normalized name
        schemes_mentioned=["Kisaan Nyay Yojana"],  # LLM identified specific scheme
        word_buckets=["Agriculture", "Welfare"],
        cognitive_view={
            "reasoning": "LLM detected policy announcement context based on 'announced new scheme' phrasing",
            "confidence": 0.85,
            "corrections": {
                "people": "Normalized 'CM Baghel' to 'Bhupesh Baghel'",
                "schemes": "Identified specific scheme 'Kisaan Nyay Yojana' instead of generic 'Irrigation Scheme'"
            }
        },
        overall_confidence=0.85,
        needs_review=True,
        review_status="pending"
    )
    test_db.add(parsed_event)
    await test_db.commit()
    return parsed_event


# TEST 1: /api/review/compare
@pytest.mark.asyncio
async def test_get_review_comparison(test_parsed_event, test_token):
    """Test GET /api/review/compare endpoint returns Parser vs LLM comparison."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/review/compare?tweet_id={test_parsed_event.tweet_id}",
            headers={"Authorization": f"Bearer {test_token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert data["tweet_id"] == "test-tweet-123"
    assert "raw_text" in data
    assert "comparison" in data
    
    # Verify event_type comparison
    event_comp = data["comparison"]["event_type"]
    assert event_comp["parser"]["value"] == "Meeting"
    assert event_comp["llm"]["value"] == "Policy Announcement"
    assert event_comp["conflict"] == True  # They disagree
    
    # Verify people comparison
    people_comp = data["comparison"]["people"]
    assert "CM Baghel" in people_comp["parser"]["value"]
    assert "Bhupesh Baghel" in people_comp["llm"]["value"]
    assert people_comp["conflict"] == True


@pytest.mark.asyncio
async def test_get_review_comparison_not_found(test_token):
    """Test 404 when tweet doesn't exist."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/review/compare?tweet_id=nonexistent",
            headers={"Authorization": f"Bearer {test_token}"}
        )
    
    assert response.status_code == 404


# TEST 2: /api/review/ask-ai
@pytest.mark.asyncio
async def test_ask_ai(test_parsed_event, test_token):
    """Test POST /api/review/ask-ai returns AI explanation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/review/ask-ai",
            json={
                "tweet_id": test_parsed_event.tweet_id,
                "question": "Why did LLM choose Policy Announcement instead of Meeting?"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data
    
    # Answer should reference cognitive_view
    assert "policy announcement" in data["answer"].lower() or "reasoning" in data["answer"].lower()
    assert data["confidence"] > 0.0


@pytest.mark.asyncio
async def test_ask_ai_with_cognitive_view(test_parsed_event, test_token):
    """Test Ask AI uses cognitive_view from enrichment."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/review/ask-ai",
            json={
                "tweet_id": test_parsed_event.tweet_id,
                "question": "What is the reasoning for LLM's choice?"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
    
    data = response.json()
    
    # Should include reasoning from cognitive_view
    assert "announced new scheme" in data["answer"].lower() or "policy" in data["answer"].lower()
    
    # Sources should include cognitive_view
    assert any(src["type"] == "cognitive_view" for src in data["sources"])


# TEST 3: /api/events/approve (Updated)
@pytest.mark.asyncio
async def test_approve_event_with_feedback(test_parsed_event, test_token, test_db):
    """Test POST /api/events/approve saves final_data and feedback_log."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/events/approve",
            json={
                "tweet_id": test_parsed_event.tweet_id,
                "final_data": {
                    "event_type": "Policy Announcement",  # Chose LLM
                    "people_canonical": ["Bhupesh Baghel"],  # Chose LLM
                    "schemes_mentioned": ["Kisaan Nyay Yojana"]  # Chose LLM
                },
                "feedback": {
                    "event_type": {"choice": "llm_win", "disagreement_strength": 1.0},
                    "people": {"choice": "llm_win", "disagreement_strength": 0.5},
                    "schemes": {"choice": "llm_win", "disagreement_strength": 1.0}
                },
                "session_id": "test-session-456",
                "review_time_sec": 42
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    
    # Verify database update
    await test_db.refresh(test_parsed_event)
    assert test_parsed_event.final_data is not None
    assert test_parsed_event.final_data["event_type"] == "Policy Announcement"
    assert test_parsed_event.feedback_log is not None
    assert test_parsed_event.feedback_log["event_type"]["choice"] == "llm_win"
    assert test_parsed_event.review_status == "approved"
    assert test_parsed_event.reviewed_by == "testuser"


@pytest.mark.asyncio
async def test_approve_event_mixed_feedback(test_parsed_event, test_token, test_db):
    """Test approval with mixed Parser/LLM choices."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/events/approve",
            json={
                "tweet_id": test_parsed_event.tweet_id,
                "final_data": {
                    "event_type": "Meeting",  # Chose Parser
                    "people_canonical": ["Bhupesh Baghel"]  # Chose LLM
                },
                "feedback": {
                    "event_type": {"choice": "parser_win"},
                    "people": {"choice": "llm_win"}
                }
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
    
    assert response.status_code == 200
    
    await test_db.refresh(test_parsed_event)
    assert test_parsed_event.feedback_log["event_type"]["choice"] == "parser_win"
    assert test_parsed_event.feedback_log["people"]["choice"] == "llm_win"


# TEST 4: Authorization
@pytest.mark.asyncio
async def test_compare_requires_auth():
    """Test /api/review/compare requires authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/review/compare?tweet_id=test-tweet-123")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ask_ai_requires_auth():
    """Test /api/review/ask-ai requires authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/review/ask-ai",
            json={"tweet_id": "test-tweet-123", "question": "Why?"}
        )
    
    assert response.status_code == 401
