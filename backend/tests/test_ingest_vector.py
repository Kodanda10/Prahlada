"""
Integration tests for data ingestion and vector search endpoints.

Tests cover:
- Ingest parsed tweet endpoint (/api/ingest-parsed-tweet)
- Vector indexing trigger endpoint (/api/vector/trigger-batch-indexing)
"""

import os
import pytest
from datetime import datetime

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from httpx import AsyncClient
from backend.tests.conftest import create_test_tweet_data


class TestIngestParsedTweetEndpoint:
    """Tests for the ingest parsed tweet endpoint."""

    @pytest.mark.asyncio
    async def test_ingest_requires_auth(self, async_client: AsyncClient):
        """Ingest endpoint should require authentication."""
        payload = create_test_tweet_data()
        
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=payload,
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_ingest_new_tweet_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should successfully ingest a new tweet."""
        payload = create_test_tweet_data(
            tweet_id="new-tweet-123",
            text="A brand new tweet about government initiatives",
        )
        
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=payload,
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["status"] == "success"
        assert "new-tweet-123" in data["message"]

    @pytest.mark.asyncio
    async def test_ingest_duplicate_tweet_skipped(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Duplicate tweet should be skipped."""
        # tweet-001 exists in test fixtures
        payload = create_test_tweet_data(
            tweet_id="tweet-001",
            text="Existing tweet text",
        )
        
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=payload,
            headers=auth_headers,
        )
        
        # Should return success but with skipped status
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_ingest_tweet_structure_validation(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should validate tweet payload structure."""
        # Missing required tweet fields
        invalid_payload = {
            "tweet": {
                "id": "test-123",
                # Missing: text, created_at, author_id
            },
            "categories": {},
            "gemini_metadata": {"model": "test", "confidence": 0.5},
        }
        
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=invalid_payload,
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ingest_missing_categories(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should validate categories presence."""
        invalid_payload = {
            "tweet": {
                "id": "test-123",
                "text": "Test tweet",
                "created_at": datetime.utcnow().isoformat(),
                "author_id": "author-1",
            },
            # Missing: categories
            "gemini_metadata": {"model": "test", "confidence": 0.5},
        }
        
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=invalid_payload,
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ingest_missing_metadata(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should validate gemini_metadata presence."""
        invalid_payload = {
            "tweet": {
                "id": "test-123",
                "text": "Test tweet",
                "created_at": datetime.utcnow().isoformat(),
                "author_id": "author-1",
            },
            "categories": {},
            # Missing: gemini_metadata
        }
        
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=invalid_payload,
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ingest_with_all_categories(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should handle all category types."""
        payload = {
            "tweet": {
                "id": "comprehensive-tweet",
                "text": "Tweet with all categories",
                "created_at": datetime.utcnow().isoformat(),
                "author_id": "author-1",
            },
            "categories": {
                "locations": ["Raipur", "Bilaspur"],
                "people": ["CM", "Minister"],
                "event": ["inauguration", "meeting"],
                "organisation": ["State Govt"],
                "schemes": ["PM Awas", "Ujjwala"],
                "communities": ["Farmers"],
            },
            "gemini_metadata": {
                "model": "gemini-pro",
                "confidence": 0.92,
            },
        }
        
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=payload,
            headers=auth_headers,
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_ingest_with_empty_categories(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should handle empty category arrays."""
        payload = {
            "tweet": {
                "id": "minimal-tweet",
                "text": "Tweet with minimal categories",
                "created_at": datetime.utcnow().isoformat(),
                "author_id": "author-1",
            },
            "categories": {
                "locations": [],
                "people": [],
                "event": [],
                "organisation": [],
                "schemes": [],
                "communities": [],
            },
            "gemini_metadata": {
                "model": "gemini-pro",
                "confidence": 0.5,
            },
        }
        
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=payload,
            headers=auth_headers,
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_ingest_confidence_range(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should accept confidence values in valid range."""
        for confidence in [0.0, 0.5, 1.0]:
            payload = {
                "tweet": {
                    "id": f"confidence-{confidence}",
                    "text": "Test tweet",
                    "created_at": datetime.utcnow().isoformat(),
                    "author_id": "author-1",
                },
                "categories": {},
                "gemini_metadata": {
                    "model": "gemini-pro",
                    "confidence": confidence,
                },
            }
            
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=payload,
                headers=auth_headers,
            )
            
            assert response.status_code == 201


class TestVectorBatchIndexingEndpoint:
    """Tests for the vector batch indexing endpoint."""

    @pytest.mark.asyncio
    async def test_vector_indexing_requires_auth(self, async_client: AsyncClient):
        """Vector indexing should require authentication."""
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={"tweetIds": ["tweet-001"]},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_vector_indexing_with_valid_ids(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should trigger indexing for valid tweet IDs."""
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={"tweetIds": ["tweet-001", "tweet-002"]},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["service"] == "faiss"

    @pytest.mark.asyncio
    async def test_vector_indexing_empty_ids(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Empty tweet ID list should be skipped."""
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={"tweetIds": []},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_vector_indexing_nonexistent_ids(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Nonexistent tweet IDs should be skipped."""
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={"tweetIds": ["nonexistent-1", "nonexistent-2"]},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_vector_indexing_missing_payload(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Missing tweetIds should return validation error."""
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={},
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_vector_indexing_invalid_payload_type(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Invalid tweetIds type should return validation error."""
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={"tweetIds": "not-an-array"},
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_vector_indexing_mixed_ids(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should handle mix of existing and nonexistent IDs."""
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={"tweetIds": ["tweet-001", "nonexistent"]},
            headers=auth_headers,
        )
        
        # Should succeed with at least one valid ID
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_vector_indexing_large_batch(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should handle large batch of IDs."""
        # Create a large list of IDs (most won't exist)
        large_id_list = [f"tweet-{i}" for i in range(100)]
        
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={"tweetIds": large_id_list},
            headers=auth_headers,
        )
        
        # Should return 200 even if most IDs don't exist
        assert response.status_code == 200


class TestIngestAndIndexFlow:
    """End-to-end tests for ingest and index flow."""

    @pytest.mark.asyncio
    async def test_ingest_then_index(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should be able to ingest a tweet and then trigger indexing."""
        # Step 1: Ingest new tweet
        tweet_id = "flow-test-tweet"
        ingest_payload = create_test_tweet_data(
            tweet_id=tweet_id,
            text="Flow test tweet content",
        )
        
        ingest_response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=ingest_payload,
            headers=auth_headers,
        )
        
        assert ingest_response.status_code == 201
        
        # Step 2: Trigger indexing for the new tweet
        index_response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json={"tweetIds": [tweet_id]},
            headers=auth_headers,
        )
        
        assert index_response.status_code == 200
        # Note: The mock vector store will handle this without actual ML processing
