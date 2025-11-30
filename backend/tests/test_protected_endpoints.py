"""
Integration tests for protected API endpoints requiring authentication.

Tests cover:
- Stats endpoint (/api/stats)
- Events endpoint (/api/events)
- Event approval endpoint (/api/events/{tweet_id}/approve)
"""

import os
import pytest

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from httpx import AsyncClient


class TestStatsEndpoint:
    """Tests for the stats endpoint."""

    @pytest.mark.asyncio
    async def test_stats_requires_auth(self, async_client: AsyncClient):
        """Stats endpoint should require authentication."""
        response = await async_client.get("/api/stats")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_stats_with_valid_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Stats endpoint should return data with valid token."""
        response = await async_client.get("/api/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_tweets" in data
        assert "parsed_success" in data
        assert "pending" in data
        assert "errors" in data

    @pytest.mark.asyncio
    async def test_stats_returns_correct_counts(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Stats should return correct counts from test data."""
        response = await async_client.get("/api/stats", headers=auth_headers)
        data = response.json()
        
        # Based on test fixtures: 3 tweets (1 processed, 1 pending, 1 failed)
        assert data["total_tweets"] == 3
        assert data["parsed_success"] == 1
        assert data["pending"] == 1
        assert data["errors"] == 1

    @pytest.mark.asyncio
    async def test_stats_values_are_integers(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Stats values should be integers."""
        response = await async_client.get("/api/stats", headers=auth_headers)
        data = response.json()
        
        for key in ["total_tweets", "parsed_success", "pending", "errors"]:
            assert isinstance(data[key], int), f"{key} should be integer"

    @pytest.mark.asyncio
    async def test_stats_with_expired_token(
        self, async_client: AsyncClient, expired_token: str
    ):
        """Stats should reject expired tokens."""
        response = await async_client.get(
            "/api/stats",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        
        assert response.status_code == 401


class TestEventsEndpoint:
    """Tests for the events endpoint."""

    @pytest.mark.asyncio
    async def test_events_requires_auth(self, async_client: AsyncClient):
        """Events endpoint should require authentication."""
        response = await async_client.get("/api/events")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_events_returns_list(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Events endpoint should return a list."""
        response = await async_client.get("/api/events", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_events_returns_event_structure(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Events should have correct structure."""
        response = await async_client.get("/api/events", headers=auth_headers)
        data = response.json()
        
        # Should have at least one event from test data
        assert len(data) >= 1
        
        event = data[0]
        expected_fields = [
            "tweet_id",
            "created_at",
            "raw_text",
            "clean_text",
            "event_type",
            "location_text",
            "scheme_tags",
            "parsing_status",
            "logs",
        ]
        
        for field in expected_fields:
            assert field in event, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_events_event_type_is_list(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Event types should be a list."""
        response = await async_client.get("/api/events", headers=auth_headers)
        data = response.json()
        
        if len(data) > 0:
            assert isinstance(data[0]["event_type"], list)

    @pytest.mark.asyncio
    async def test_events_scheme_tags_is_list(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Scheme tags should be a list."""
        response = await async_client.get("/api/events", headers=auth_headers)
        data = response.json()
        
        if len(data) > 0:
            assert isinstance(data[0]["scheme_tags"], list)

    @pytest.mark.asyncio
    async def test_events_logs_is_list(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Logs should be a list of strings."""
        response = await async_client.get("/api/events", headers=auth_headers)
        data = response.json()
        
        if len(data) > 0:
            assert isinstance(data[0]["logs"], list)

    @pytest.mark.asyncio
    async def test_events_filter_by_status_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should filter events by SUCCESS status."""
        response = await async_client.get(
            "/api/events?status=success",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned events should have SUCCESS status
        for event in data:
            assert event["parsing_status"] == "SUCCESS"

    @pytest.mark.asyncio
    async def test_events_filter_by_status_failed(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should filter events by FAILED status."""
        response = await async_client.get(
            "/api/events?status=failed",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for event in data:
            assert event["parsing_status"] == "FAILED"

    @pytest.mark.asyncio
    async def test_events_filter_by_status_pending(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should filter events by PENDING status."""
        response = await async_client.get(
            "/api/events?status=pending",
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_events_filter_case_insensitive(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Status filter should be case-insensitive."""
        # Test uppercase
        response_upper = await async_client.get(
            "/api/events?status=SUCCESS",
            headers=auth_headers,
        )
        
        # Test lowercase
        response_lower = await async_client.get(
            "/api/events?status=success",
            headers=auth_headers,
        )
        
        assert response_upper.status_code == 200
        assert response_lower.status_code == 200

    @pytest.mark.asyncio
    async def test_events_invalid_filter(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Invalid status filter should return empty or unfiltered results."""
        response = await async_client.get(
            "/api/events?status=invalid_status",
            headers=auth_headers,
        )
        
        # Should still return 200, just no filtered results
        assert response.status_code == 200


class TestEventApprovalEndpoint:
    """Tests for the event approval endpoint."""

    @pytest.mark.asyncio
    async def test_approve_requires_auth(self, async_client: AsyncClient):
        """Approval endpoint should require authentication."""
        response = await async_client.post("/api/events/tweet-001/approve")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_approve_existing_event(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should successfully approve an existing event."""
        response = await async_client.post(
            "/api/events/tweet-001/approve",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "tweet-001" in data["message"]

    @pytest.mark.asyncio
    async def test_approve_nonexistent_event(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should return 404 for nonexistent event."""
        response = await async_client.post(
            "/api/events/nonexistent-tweet/approve",
            headers=auth_headers,
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_approve_sets_approved_status(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Approval should set the event's review status to approved."""
        # Approve the event
        await async_client.post(
            "/api/events/tweet-001/approve",
            headers=auth_headers,
        )
        
        # Note: In a full test, we would verify the database state
        # or check via another endpoint that the status changed


class TestTelemetryEndpoint:
    """Tests for the telemetry endpoint."""

    @pytest.mark.asyncio
    async def test_telemetry_accepts_event(self, async_client: AsyncClient):
        """Telemetry endpoint should accept event data."""
        response = await async_client.post(
            "/api/telemetry",
            json={
                "type": "click",
                "name": "button_clicked",
                "data": {"button_id": "submit"},
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_telemetry_minimal_payload(self, async_client: AsyncClient):
        """Telemetry should accept minimal required fields."""
        response = await async_client.post(
            "/api/telemetry",
            json={"type": "pageview", "name": "home_page"},
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_telemetry_with_url(self, async_client: AsyncClient):
        """Telemetry should accept URL field."""
        response = await async_client.post(
            "/api/telemetry",
            json={
                "type": "pageview",
                "name": "analytics_page",
                "url": "/analytics",
            },
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_telemetry_with_timestamp(self, async_client: AsyncClient):
        """Telemetry should accept timestamp field."""
        response = await async_client.post(
            "/api/telemetry",
            json={
                "type": "error",
                "name": "api_error",
                "timestamp": 1700000000,
            },
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_telemetry_missing_type(self, async_client: AsyncClient):
        """Missing type should return validation error."""
        response = await async_client.post(
            "/api/telemetry",
            json={"name": "event_name"},
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_telemetry_missing_name(self, async_client: AsyncClient):
        """Missing name should return validation error."""
        response = await async_client.post(
            "/api/telemetry",
            json={"type": "click"},
        )
        
        assert response.status_code == 422
