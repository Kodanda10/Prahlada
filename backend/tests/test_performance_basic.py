"""
Basic performance and load-safety tests for backend endpoints.

Tests verify endpoints behave well under basic load without exponential slowdown.
These are lightweight integration tests, not full load testing.
"""

import os
import time
import pytest
import asyncio
from typing import List

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from httpx import AsyncClient


class TestEndpointLoadSafety:
    """Tests for endpoint behavior under basic load."""

    @pytest.fixture
    async def auth_headers(self, async_client: AsyncClient):
        """Get authentication headers for tests."""
        # Login to get token
        login_response = await async_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_stats_endpoint_load_safety(self, async_client: AsyncClient, auth_headers: dict):
        """Stats endpoint should handle multiple sequential requests efficiently."""
        # Make 10 requests in sequence
        start_time = time.time()
        response_times: List[float] = []

        for i in range(10):
            request_start = time.time()
            response = await async_client.get("/api/stats", headers=auth_headers)
            request_end = time.time()

            assert response.status_code == 200
            response_times.append(request_end - request_start)

        total_time = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        # Basic sanity checks - no exponential slowdown
        # Average should be reasonable (< 1 second)
        assert avg_response_time < 1.0, f"Average response time too high: {avg_response_time:.3f}s"

        # Max should not be excessively high (< 2 seconds)
        assert max_response_time < 2.0, f"Max response time too high: {max_response_time:.3f}s"

        # Should complete all requests in reasonable time (< 5 seconds total)
        assert total_time < 5.0, f"Total time too high: {total_time:.3f}s"

    @pytest.mark.asyncio
    async def test_events_endpoint_load_safety(self, async_client: AsyncClient, auth_headers: dict):
        """Events endpoint should handle multiple requests efficiently."""
        start_time = time.time()
        response_times: List[float] = []

        for i in range(5):  # Fewer requests for events as it may be heavier
            request_start = time.time()
            response = await async_client.get("/api/events", headers=auth_headers)
            request_end = time.time()

            assert response.status_code == 200
            response_times.append(request_end - request_start)

        total_time = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        # Events endpoint might be heavier, allow slightly higher thresholds
        assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 3.0, f"Max response time too high: {max_response_time:.3f}s"
        assert total_time < 8.0, f"Total time too high: {total_time:.3f}s"

    @pytest.mark.asyncio
    async def test_search_endpoint_load_safety(self, async_client: AsyncClient, auth_headers: dict):
        """Search endpoint should handle multiple queries efficiently."""
        queries = [
            "government scheme",
            "education policy",
            "healthcare initiative",
            "rural development",
            "digital transformation"
        ]

        start_time = time.time()
        response_times: List[float] = []

        for query in queries:
            request_start = time.time()
            response = await async_client.post(
                "/api/search",
                json={"query": query, "k": 3},
                headers=auth_headers
            )
            request_end = time.time()

            assert response.status_code == 200
            response_times.append(request_end - request_start)

        total_time = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        # Search might involve vector operations, allow higher thresholds
        assert avg_response_time < 3.0, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 5.0, f"Max response time too high: {max_response_time:.3f}s"
        assert total_time < 12.0, f"Total time too high: {total_time:.3f}s"

    @pytest.mark.asyncio
    async def test_ingest_endpoint_load_safety(self, async_client: AsyncClient, auth_headers: dict):
        """Ingest endpoint should handle multiple ingestion requests."""
        # Create different tweet payloads
        payloads = []
        for i in range(3):
            payload = {
                "tweet": {
                    "id": f"load-test-tweet-{i}",
                    "text": f"Load test tweet content {i}",
                    "created_at": "2024-01-01T00:00:00",
                    "author_id": f"user-{i}",
                },
                "categories": {
                    "event": ["test_event"],
                    "locations": ["test_location"],
                    "schemes": ["test_scheme"]
                },
                "gemini_metadata": {
                    "model": "test-model",
                    "confidence": 0.8
                }
            }
            payloads.append(payload)

        start_time = time.time()
        response_times: List[float] = []

        for payload in payloads:
            request_start = time.time()
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=payload,
                headers=auth_headers
            )
            request_end = time.time()

            # Should succeed (201) or be duplicate (200)
            assert response.status_code in [200, 201]
            response_times.append(request_end - request_start)

        total_time = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        # Ingest involves DB writes, allow reasonable thresholds
        assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 3.0, f"Max response time too high: {max_response_time:.3f}s"
        assert total_time < 6.0, f"Total time too high: {total_time:.3f}s"


class TestConcurrentLoadSafety:
    """Tests for concurrent request handling."""

    @pytest.fixture
    async def auth_headers(self, async_client: AsyncClient):
        """Get authentication headers for tests."""
        login_response = await async_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_concurrent_stats_requests(self, async_client: AsyncClient, auth_headers: dict):
        """Should handle concurrent stats requests without issues."""
        async def make_request():
            response = await async_client.get("/api/stats", headers=auth_headers)
            assert response.status_code == 200
            return response.json()

        # Launch 5 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # All should succeed and return data
        assert len(results) == 5
        for result in results:
            assert "total_tweets" in result

        # Should complete reasonably fast (concurrent should be faster than sequential)
        assert total_time < 3.0, f"Concurrent requests took too long: {total_time:.3f}s"

    @pytest.mark.asyncio
    async def test_concurrent_search_requests(self, async_client: AsyncClient, auth_headers: dict):
        """Should handle concurrent search requests."""
        async def make_search_request(query: str):
            response = await async_client.post(
                "/api/search",
                json={"query": query, "k": 2},
                headers=auth_headers
            )
            assert response.status_code == 200
            return response.json()

        queries = ["policy", "scheme", "development", "education"]
        start_time = time.time()
        tasks = [make_search_request(query) for query in queries]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        assert len(results) == 4
        for result in results:
            assert isinstance(result, list)  # Search returns list of results

        # Should complete in reasonable time
        assert total_time < 8.0, f"Concurrent search took too long: {total_time:.3f}s"


class TestMemoryAndResourceSafety:
    """Tests for memory usage and resource cleanup."""

    @pytest.fixture
    async def auth_headers(self, async_client: AsyncClient):
        """Get authentication headers."""
        login_response = await async_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_large_response_handling(self, async_client: AsyncClient, auth_headers: dict):
        """Should handle endpoints that return larger responses."""
        # Events endpoint might return more data
        response = await async_client.get("/api/events", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should be a list, even if empty
        assert isinstance(data, list)

        # Response shouldn't be excessively large in test environment
        # (This is a basic sanity check)
        response_size = len(str(data))
        assert response_size < 1000000, f"Response too large: {response_size} characters"

    @pytest.mark.asyncio
    async def test_analytics_endpoints_load(self, async_client: AsyncClient, auth_headers: dict):
        """Analytics endpoints should handle load reasonably."""
        # Test a few different chart types
        chart_types = ["location_distribution", "event_trends", "scheme_popularity"]

        start_time = time.time()
        response_times: List[float] = []

        for chart_type in chart_types:
            request_start = time.time()
            response = await async_client.get(
                f"/api/analytics/{chart_type}",
                headers=auth_headers
            )
            request_end = time.time()

            assert response.status_code == 200
            response_times.append(request_end - request_start)

        total_time = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times)

        # Analytics queries might be complex, allow reasonable thresholds
        assert avg_response_time < 3.0, f"Average analytics response time too high: {avg_response_time:.3f}s"
        assert total_time < 7.0, f"Total analytics time too high: {total_time:.3f}s"