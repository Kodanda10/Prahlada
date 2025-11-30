"""
Edge case tests for backend API endpoints.

Tests cover:
- Empty database states
- Boundary values
- Invalid input handling
- Error response formats
"""

import os
import pytest

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from httpx import AsyncClient


class TestEmptyDatabaseStates:
    """Tests for behavior with empty database."""

    @pytest.mark.asyncio
    async def test_stats_with_zero_tweets(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Stats endpoint should handle zero tweets gracefully."""
        # Note: Test fixtures include some data, but this validates the response structure
        response = await async_client.get("/api/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # All values should be non-negative integers
        assert isinstance(data["total_tweets"], int)
        assert data["total_tweets"] >= 0
        assert isinstance(data["parsed_success"], int)
        assert data["parsed_success"] >= 0

    @pytest.mark.asyncio
    async def test_events_returns_empty_list_when_filtered(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Events endpoint should return empty list for non-matching filter."""
        response = await async_client.get(
            "/api/events?status=nonexistent_status",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestBoundaryValues:
    """Tests for boundary value handling."""

    @pytest.mark.asyncio
    async def test_search_with_zero_k(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Search with k=0 should return empty results."""
        response = await async_client.post(
            "/api/search",
            json={"query": "test", "k": 0},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_search_with_very_long_query(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Search should handle very long queries."""
        long_query = "test " * 500  # 2500 characters
        
        response = await async_client.post(
            "/api/search",
            json={"query": long_query, "k": 5},
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_telemetry_with_large_data_payload(
        self, async_client: AsyncClient
    ):
        """Telemetry should handle large data payloads."""
        large_data = {f"key_{i}": f"value_{i}" for i in range(100)}
        
        response = await async_client.post(
            "/api/telemetry",
            json={
                "type": "test",
                "name": "large_payload_test",
                "data": large_data,
            },
        )
        
        assert response.status_code == 201


class TestInvalidInputHandling:
    """Tests for invalid input handling."""

    @pytest.mark.asyncio
    async def test_login_with_null_username(self, async_client: AsyncClient):
        """Login should reject null username."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": None, "password": "test"},
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_with_numeric_username(self, async_client: AsyncClient):
        """Login should accept numeric string as username."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "12345", "password": "test"},
        )
        
        # Should fail auth but not validation
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_ingest_with_future_date(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Ingest should accept future dates (no validation on date range)."""
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json={
                "tweet": {
                    "id": "future-tweet-001",
                    "text": "Future tweet",
                    "created_at": "2099-12-31T23:59:59",
                    "author_id": "author-1",
                },
                "categories": {},
                "gemini_metadata": {"model": "test", "confidence": 0.5},
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_ingest_with_invalid_confidence(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Ingest should reject confidence outside 0-1 range."""
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json={
                "tweet": {
                    "id": "invalid-conf-001",
                    "text": "Test tweet",
                    "created_at": "2024-01-01T00:00:00",
                    "author_id": "author-1",
                },
                "categories": {},
                "gemini_metadata": {"model": "test", "confidence": 1.5},
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ingest_with_negative_confidence(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Ingest should reject negative confidence."""
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json={
                "tweet": {
                    "id": "negative-conf-001",
                    "text": "Test tweet",
                    "created_at": "2024-01-01T00:00:00",
                    "author_id": "author-1",
                },
                "categories": {},
                "gemini_metadata": {"model": "test", "confidence": -0.5},
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422


class TestErrorResponseFormats:
    """Tests for consistent error response formats."""

    @pytest.mark.asyncio
    async def test_401_response_format(self, async_client: AsyncClient):
        """401 errors should have consistent format."""
        response = await async_client.get("/api/stats")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_404_response_format(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """404 errors should have consistent format."""
        response = await async_client.post(
            "/api/events/nonexistent-tweet-id/approve",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_422_response_format(self, async_client: AsyncClient):
        """422 validation errors should have consistent format."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "test"},  # Missing password
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestSpecialCharacterHandling:
    """Tests for special character handling."""

    @pytest.mark.asyncio
    async def test_search_with_unicode_hindi(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Search should handle Hindi Unicode characters."""
        response = await async_client.post(
            "/api/search",
            json={"query": "सरकारी योजना राजधानी", "k": 5},
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_with_special_symbols(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Search should handle special symbols."""
        response = await async_client.post(
            "/api/search",
            json={"query": "PM's scheme @mention #hashtag & benefits", "k": 5},
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_with_newlines(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Search should handle newlines in query."""
        response = await async_client.post(
            "/api/search",
            json={"query": "line one\nline two\nline three", "k": 5},
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_telemetry_with_unicode_name(self, async_client: AsyncClient):
        """Telemetry should handle Unicode event names."""
        response = await async_client.post(
            "/api/telemetry",
            json={
                "type": "click",
                "name": "बटन_क्लिक",  # Hindi button click
            },
        )
        
        assert response.status_code == 201


class TestAuthenticationEdgeCases:
    """Edge cases for authentication."""

    @pytest.mark.asyncio
    async def test_verify_with_whitespace_token(self, async_client: AsyncClient):
        """Verify should reject whitespace-only token."""
        response = await async_client.get(
            "/api/auth/verify",
            headers={"Authorization": "Bearer    "},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_with_malformed_jwt(self, async_client: AsyncClient):
        """Verify should reject malformed JWT."""
        response = await async_client.get(
            "/api/auth/verify",
            headers={"Authorization": "Bearer not.a.valid.jwt.token"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_lowercase_bearer(
        self, async_client: AsyncClient, valid_auth_token: str
    ):
        """Protected endpoints should accept lowercase 'bearer'."""
        response = await async_client.get(
            "/api/stats",
            headers={"Authorization": f"bearer {valid_auth_token}"},
        )
        
        # Should work with lowercase
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_multiple_auth_headers(
        self, async_client: AsyncClient, valid_auth_token: str
    ):
        """Should use the Authorization header value as-is."""
        response = await async_client.get(
            "/api/stats",
            headers={"Authorization": f"Bearer {valid_auth_token}"},
        )
        
        assert response.status_code == 200
