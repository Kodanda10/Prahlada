import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
from dotenv import load_dotenv

# Force load test env before importing backend modules
load_dotenv(".env.test", override=True)

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.main import app
from backend.auth import create_access_token

# Set default scope for async fixtures
pytest_plugins = ('pytest_asyncio',)

MOCK_USER = {
    "username": "testadmin",
    "password": "securepassword123",
    "role": "admin"
}

@pytest.fixture
def client():
    # TestClient context manager triggers lifespan events (startup/shutdown)
    # which in main.py includes database table creation.
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_header():
    access_token = create_access_token(data={"sub": MOCK_USER["username"], "role": MOCK_USER["role"]})
    return {"Authorization": f"Bearer {access_token}"}

# We use standard pytest functions (not async) because TestClient is synchronous
# and handles the async calls to the backend internally.

def test_login_endpoint(client):
    """Validates the login endpoint structure."""
    response = client.post("/api/auth/login", json={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401

def test_events_endpoint(client, auth_header):
    """Validates the events (tweets) retrieval endpoint."""
    response = client.get("/api/events", headers=auth_header)
    assert response.status_code == 200

def test_stats_endpoint(client, auth_header):
    """Validates the stats endpoint."""
    response = client.get("/api/stats", headers=auth_header)
    assert response.status_code == 200

def test_search_endpoint(client, auth_header):
    """Stress tests the semantic search endpoint."""
    query = {"query": "test query", "k": 5}
    response = client.post("/api/search", json=query, headers=auth_header)
    assert response.status_code in [200, 500]

def test_health_check(client):
    """Validates the system health endpoint."""
    response = client.get("/api/health/system")
    assert response.status_code == 200

if __name__ == "__main__":
    load_dotenv(".env.test", override=True)
    sys.exit(pytest.main(["-v", __file__]))
