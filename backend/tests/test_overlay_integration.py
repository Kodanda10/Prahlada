"""
Overlay Service Integration Tests.

Tests the integration between overlay service, cognitive engine,
review workflows, and API endpoints.
"""

import os
import json
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.overlay_service import OverlayService, OverlayRecord
from backend.tests.conftest import create_test_tweet_data


@pytest.mark.asyncio
class TestOverlayIntegration:
    """
    Integration tests for overlay service with cognitive engine and review workflows.
    """

    @pytest.fixture
    def overlay_service(self, tmp_path):
        """Overlay service instance for integration testing."""
        overlay_dir = tmp_path / "integration_overlays"
        overlay_dir.mkdir()
        return OverlayService(str(overlay_dir))

    async def test_overlay_cognitive_engine_feedback_loop(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService,
        mock_cognitive_engine
    ):
        """
        Test overlay corrections feeding back into cognitive engine learning.
        """
        # Setup cognitive engine to learn from corrections
        learning_calls = []

        def mock_process_correction(tweet_id, text, old_data, correction):
            learning_calls.append({
                "tweet_id": tweet_id,
                "old_data": old_data,
                "correction": correction
            })
            return {
                "id": f"learn-{len(learning_calls)}",
                "decision": {"action": "approve", "confidence": 0.95},
                "details": {"learned": True, "pattern": "location_correction"}
            }

        mock_cognitive_engine.process_correction.side_effect = mock_process_correction

        # Step 1: Ingest tweet with initial parsing
        tweet_data = create_test_tweet_data(
            tweet_id="integration-cognitive-001",
            text="रायपुर शहर में मुख्यमंत्री कार्यालय के पास विकास कार्य शुरू हुए।"
        )

        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=tweet_data,
            headers=auth_headers
        )
        assert response.status_code == 201

        # Step 2: Apply overlay correction
        overlay_service.add_overlay(
            tweet_id="integration-cognitive-001",
            field="location",
            corrected_value="Raipur City",
            reviewer_id="integration-reviewer",
            confidence=0.9,
            notes="Precise location correction for cognitive learning"
        )

        # Step 3: Trigger cognitive correction process
        correction_payload = {
            "tweet_id": "integration-cognitive-001",
            "text": "रायपुर शहर में मुख्यमंत्री कार्यालय के पास विकास कार्य शुरू हुए।",
            "old_data": {"location": "Raipur"},
            "correction": {"location": "Raipur City"}
        }

        response = await async_client.post(
            "/api/cognitive/correct",
            json=correction_payload,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Step 4: Verify cognitive engine received correction data
        assert len(learning_calls) == 1
        call_data = learning_calls[0]
        assert call_data["tweet_id"] == "integration-cognitive-001"
        assert call_data["correction"]["location"] == "Raipur City"

        # Step 5: Verify overlay data is preserved
        overlays = overlay_service.get_overlays_for_tweet("integration-cognitive-001")
        assert len(overlays) == 1
        assert overlays[0].corrected_value == "Raipur City"

    async def test_overlay_review_workflow_integration(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Test overlay corrections integrated with review workflow approval process.
        """
        # Step 1: Ingest tweets requiring review
        review_tweets = [
            create_test_tweet_data(
                tweet_id="review-workflow-001",
                text="मुख्यमंत्री ने राज्य स्तरीय विकास समिति की बैठक में महत्वपूर्ण निर्णय लिए।"
            ),
            create_test_tweet_data(
                tweet_id="review-workflow-002",
                text="रायपुर में शिक्षा विभाग के अधिकारियों के साथ समीक्षा बैठक संपन्न हुई।"
            ),
        ]

        for tweet_data in review_tweets:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code == 201

        # Step 2: Get events to review
        response = await async_client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200
        events = response.json()

        # Step 3: Apply overlay corrections before approval
        overlay_service.add_overlay(
            tweet_id="review-workflow-001",
            field="event_type",
            corrected_value="committee_meeting",
            reviewer_id="workflow-reviewer",
            confidence=0.92,
            notes="Corrected event type before approval"
        )

        overlay_service.add_overlay(
            tweet_id="review-workflow-002",
            field="location",
            corrected_value="Raipur, Chhattisgarh",
            reviewer_id="workflow-reviewer",
            confidence=0.88,
            notes="Enhanced location precision before approval"
        )

        # Step 4: Approve events (simulating review workflow)
        for tweet_id in ["review-workflow-001", "review-workflow-002"]:
            response = await async_client.post(
                f"/api/events/{tweet_id}/approve",
                headers=auth_headers
            )
            assert response.status_code == 200

        # Step 5: Verify overlays are preserved after approval
        for tweet_id in ["review-workflow-001", "review-workflow-002"]:
            overlays = overlay_service.get_overlays_for_tweet(tweet_id)
            assert len(overlays) >= 1

        # Step 6: Verify approval statistics
        overlay_stats = overlay_service.get_overlay_stats()
        assert overlay_stats["total_overlays"] >= 2

    async def test_overlay_search_integration(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService,
        mock_vector_store
    ):
        """
        Test overlay corrections improving search results and semantic matching.
        """
        # Step 1: Ingest and index tweets
        search_tweets = [
            create_test_tweet_data(
                tweet_id="search-integration-001",
                text="छत्तीसगढ़ में किसान सम्मेलन का सफल आयोजन किया गया।"
            ),
            create_test_tweet_data(
                tweet_id="search-integration-002",
                text="मुख्यमंत्री ने कृषि विकास पर जोर दिया।"
            ),
        ]

        for tweet_data in search_tweets:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code == 201

        # Step 2: Index tweets for search
        index_payload = {"tweetIds": ["search-integration-001", "search-integration-002"]}

        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json=index_payload,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Step 3: Apply overlay corrections that improve searchability
        overlay_service.add_overlay(
            tweet_id="search-integration-001",
            field="event_type",
            corrected_value="farmer_conference",
            reviewer_id="search-reviewer",
            confidence=0.9,
            notes="Improved event classification for better search"
        )

        overlay_service.add_overlay(
            tweet_id="search-integration-002",
            field="schemes",
            corrected_value="Agriculture Development",
            reviewer_id="search-reviewer",
            confidence=0.85,
            notes="Added scheme context for enhanced search results"
        )

        # Step 4: Perform semantic search
        search_payload = {"query": "किसान सम्मेलन", "k": 5}

        response = await async_client.post(
            "/api/search",
            json=search_payload,
            headers=auth_headers
        )
        assert response.status_code == 200
        search_results = response.json()

        # Search should work regardless of overlay corrections
        # (mock returns predefined results)
        assert isinstance(search_results, list)

        # Step 5: Verify overlay data integrity after search operations
        overlay_stats = overlay_service.get_overlay_stats()
        assert overlay_stats["total_overlays"] == 2
        assert overlay_stats["field_distribution"]["event_type"] == 1
        assert overlay_stats["field_distribution"]["schemes"] == 1

    async def test_overlay_telemetry_integration(
        self,
        async_client: AsyncClient,
        overlay_service: OverlayService
    ):
        """
        Test overlay operations generating appropriate telemetry events.
        """
        # Step 1: Apply overlay corrections
        overlay_service.add_overlay(
            tweet_id="telemetry-integration-001",
            field="event_type",
            corrected_value="public_meeting",
            reviewer_id="telemetry-reviewer",
            confidence=0.9,
            notes="Telemetry integration test correction"
        )

        # Step 2: Send telemetry events for overlay operations
        telemetry_payload = {
            "event_type": "overlay_correction_applied",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "tweet_id": "telemetry-integration-001",
                "field": "event_type",
                "reviewer_id": "telemetry-reviewer",
                "confidence": 0.9
            }
        }

        # Telemetry endpoint doesn't require auth
        response = await async_client.post("/api/telemetry", json=telemetry_payload)
        assert response.status_code == 201

        # Step 3: Send multiple telemetry events
        telemetry_events = [
            {
                "event_type": "overlay_batch_processed",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"batch_size": 5, "processing_time": 1.2}
            },
            {
                "event_type": "cognitive_learning_triggered",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"patterns_learned": 3, "accuracy_improvement": 0.05}
            },
        ]

        for event in telemetry_events:
            response = await async_client.post("/api/telemetry", json=event)
            assert response.status_code == 201

        # Step 4: Verify overlay data remains intact after telemetry operations
        overlays = overlay_service.get_overlays_for_tweet("telemetry-integration-001")
        assert len(overlays) == 1
        assert overlays[0].corrected_value == "public_meeting"

    async def test_overlay_error_handling_integration(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Test overlay service error handling integrated with API error responses.
        """
        # Step 1: Test invalid overlay operations
        # Try to add overlay for non-existent tweet
        overlay_service.add_overlay(
            tweet_id="nonexistent-tweet-001",
            field="event_type",
            corrected_value="test",
            reviewer_id="error-test-reviewer",
            confidence=0.8
        )

        # Step 2: Test API operations with overlay data
        # This should work even with overlay corrections
        response = await async_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200

        # Step 3: Test cognitive correction with overlay data
        correction_payload = {
            "tweet_id": "error-handling-tweet",
            "text": "Test tweet for error handling",
            "old_data": {"event_type": "unknown"},
            "correction": {"event_type": "test_event"}
        }

        response = await async_client.post(
            "/api/cognitive/correct",
            json=correction_payload,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Step 4: Verify error handling doesn't corrupt overlay data
        overlays = overlay_service.get_overlays_for_tweet("nonexistent-tweet-001")
        assert len(overlays) == 1  # Should still exist despite being for nonexistent tweet

        overlay_stats = overlay_service.get_overlay_stats()
        assert overlay_stats["total_overlays"] >= 1

    async def test_overlay_concurrent_access_integration(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Test concurrent overlay operations with API endpoint integration.
        """
        import asyncio

        # Step 1: Prepare concurrent overlay operations
        async def add_overlay_async(tweet_id: str, field: str, value: str, reviewer: str):
            overlay_service.add_overlay(
                tweet_id=tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id=reviewer,
                confidence=0.85,
                notes=f"Concurrent operation by {reviewer}"
            )
            await asyncio.sleep(0.01)  # Simulate async operation

        # Step 2: Execute concurrent overlay additions
        concurrent_tasks = [
            add_overlay_async("concurrent-tweet-001", "event_type", "meeting", "reviewer-A"),
            add_overlay_async("concurrent-tweet-001", "location", "Raipur", "reviewer-B"),
            add_overlay_async("concurrent-tweet-002", "event_type", "conference", "reviewer-A"),
            add_overlay_async("concurrent-tweet-002", "schemes", "Digital India", "reviewer-C"),
        ]

        await asyncio.gather(*concurrent_tasks)

        # Step 3: Verify concurrent operations didn't corrupt data
        overlays_tweet_1 = overlay_service.get_overlays_for_tweet("concurrent-tweet-001")
        overlays_tweet_2 = overlay_service.get_overlays_for_tweet("concurrent-tweet-002")

        assert len(overlays_tweet_1) == 2
        assert len(overlays_tweet_2) == 2

        # Step 4: Test API operations work with concurrently modified data
        response = await async_client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200

        # Step 5: Verify overlay statistics after concurrent operations
        stats = overlay_service.get_overlay_stats()
        assert stats["total_overlays"] == 4
        assert stats["tweets_with_overlays"] == 2
        assert stats["reviewer_distribution"]["reviewer-A"] == 2
        assert stats["reviewer_distribution"]["reviewer-B"] == 1
        assert stats["reviewer_distribution"]["reviewer-C"] == 1

    async def test_overlay_data_consistency_integration(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Test overlay data consistency across multiple API operations and workflows.
        """
        # Step 1: Create comprehensive test data
        consistency_tweet_id = "consistency-test-001"

        # Add multiple overlays for same tweet
        overlay_fields = ["event_type", "location", "schemes", "people"]
        overlay_values = ["public_meeting", "Raipur", "PM Awas Yojana", "CM Bhupesh Baghel"]

        for field, value in zip(overlay_fields, overlay_values):
            overlay_service.add_overlay(
                tweet_id=consistency_tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id="consistency-reviewer",
                confidence=0.9,
                notes=f"Consistency test for {field}"
            )

        # Step 2: Perform various API operations that might access overlay data
        operations = [
            lambda: async_client.get("/api/stats", headers=auth_headers),
            lambda: async_client.get("/api/events", headers=auth_headers),
            lambda: async_client.post("/api/search", json={"query": "test", "k": 1}, headers=auth_headers),
        ]

        for operation in operations:
            response = await operation()
            assert response.status_code in [200, 404]  # 404 is acceptable for some endpoints

        # Step 3: Verify overlay data consistency after operations
        overlays = overlay_service.get_overlays_for_tweet(consistency_tweet_id)
        assert len(overlays) == 4

        # Verify all fields are present
        overlay_fields_found = {o.field for o in overlays}
        assert overlay_fields_found == set(overlay_fields)

        # Verify all values are correct
        overlay_values_found = {o.corrected_value for o in overlays}
        assert overlay_values_found == set(overlay_values)

        # Step 4: Test overlay application consistency
        test_data = {field: "original_value" for field in overlay_fields}
        result = overlay_service.apply_overlays(test_data, consistency_tweet_id)

        # All fields should be corrected
        for field, expected_value in zip(overlay_fields, overlay_values):
            assert result[field] == expected_value

        # Original data should be unchanged
        for field in overlay_fields:
            assert test_data[field] == "original_value"

    async def test_overlay_performance_integration(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Test overlay service performance under load with API integration.
        """
        import time

        # Step 1: Generate performance test data
        num_overlays = 50
        performance_tweet_ids = [f"perf-tweet-{i:03d}" for i in range(num_overlays)]

        start_time = time.time()

        # Add overlays in batch
        for i, tweet_id in enumerate(performance_tweet_ids):
            overlay_service.add_overlay(
                tweet_id=tweet_id,
                field="event_type" if i % 2 == 0 else "location",
                corrected_value=f"perf-value-{i}",
                reviewer_id=f"perf-reviewer-{i % 5}",
                confidence=0.8 + (i * 0.002),  # Varying confidence
                notes=f"Performance test overlay {i}"
            )

        batch_add_time = time.time() - start_time

        # Step 2: Test retrieval performance
        start_time = time.time()

        for tweet_id in performance_tweet_ids[:10]:  # Test subset
            overlays = overlay_service.get_overlays_for_tweet(tweet_id)
            assert len(overlays) == 1

        retrieval_time = time.time() - start_time

        # Step 3: Test statistics performance
        start_time = time.time()
        stats = overlay_service.get_overlay_stats()
        stats_time = time.time() - start_time

        # Performance assertions (reasonable times for test environment)
        assert batch_add_time < 2.0  # Should complete within 2 seconds
        assert retrieval_time < 1.0  # Retrieval should be fast
        assert stats_time < 0.5     # Statistics should be very fast

        # Step 4: Verify API still works under load
        response = await async_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200

        # Step 5: Verify data integrity under load
        assert stats["total_overlays"] == num_overlays
        assert stats["tweets_with_overlays"] == num_overlays
        assert len(stats["reviewer_distribution"]) == 5  # 5 different reviewers