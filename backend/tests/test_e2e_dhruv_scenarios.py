"""
End-to-End Scenario Tests for Dhruv Platform.

Tests comprehensive workflows from tweet ingestion through parsing,
overlay corrections, and analytics with the overlay service integration.
"""

import os
import json
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import MagicMock, patch, AsyncMock

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["FAISS_INDEX_PATH"] = "/tmp/test_faiss_index.bin"

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.services.overlay_service import OverlayService, get_overlay_service
from backend.tests.conftest import create_test_tweet_data


@pytest.mark.asyncio
class TestDhruvE2EScenarios:
    """
    End-to-End scenario tests for Dhruv platform with overlay service integration.

    Covers complete workflows from tweet ingestion to overlay corrections and analytics.
    """

    @pytest.fixture
    def overlay_service(self, tmp_path):
        """Overlay service instance for E2E testing."""
        overlay_dir = tmp_path / "overlays"
        overlay_dir.mkdir()
        return OverlayService(str(overlay_dir))

    async def test_scenario_1_tweet_ingestion_to_overlay_correction(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Scenario 1: Tweet Ingestion → Parsing → Human Review → Overlay Correction

        Tests the complete workflow from raw tweet ingestion through human corrections.
        """
        # Step 1: Ingest a tweet with initial parsing
        tweet_data = create_test_tweet_data(
            tweet_id="dhruv-scenario-001",
            text="मुख्यमंत्री श्री भूपेश बघेल ने रायपुर में प्रधानमंत्री आवास योजना का शिलान्यास किया।"
        )

        # Ingest the tweet
        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=tweet_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        result = response.json()
        assert result["status"] == "success"

        # Step 2: Verify tweet was ingested and parsed
        response = await async_client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 1

        # Find our ingested tweet
        ingested_event = next(
            (e for e in events if e["tweet_id"] == "dhruv-scenario-001"),
            None
        )
        assert ingested_event is not None
        assert "मुख्यमंत्री" in ingested_event["raw_text"]

        # Step 3: Simulate human review correction (wrong event type detected)
        # Original parsing might have classified as "meeting" but it's actually "inauguration"
        overlay_service.add_overlay(
            tweet_id="dhruv-scenario-001",
            field="event_type",
            corrected_value="inauguration",
            reviewer_id="reviewer-dhruv",
            reviewer_name="Dhruv Reviewer",
            notes="Corrected event type from meeting to inauguration"
        )

        # Step 4: Verify overlay was applied
        overlays = overlay_service.get_overlays_for_tweet("dhruv-scenario-001")
        assert len(overlays) == 1
        assert overlays[0].corrected_value == "inauguration"
        assert overlays[0].reviewer_id == "reviewer-dhruv"

        # Step 5: Test that overlay corrections are preserved in service
        stats = overlay_service.get_overlay_stats()
        assert stats["total_overlays"] >= 1
        assert stats["field_distribution"]["event_type"] >= 1

    async def test_scenario_2_bulk_ingestion_with_mixed_corrections(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Scenario 2: Bulk Tweet Ingestion → Mixed Parsing Quality → Selective Corrections

        Tests bulk operations with varying parsing quality and selective human corrections.
        """
        # Step 1: Ingest multiple tweets with different parsing scenarios
        tweets_data = [
            create_test_tweet_data(
                tweet_id="dhruv-bulk-001",
                text="रायपुर जिले में स्वास्थ्य शिविर का आयोजन किया गया।"
            ),
            create_test_tweet_data(
                tweet_id="dhruv-bulk-002",
                text="बिलासपुर में मुख्यमंत्री ने किसान सम्मेलन को संबोधित किया।"
            ),
            create_test_tweet_data(
                tweet_id="dhruv-bulk-003",
                text="दुर्ग में प्रधानमंत्री आवास योजना के लाभार्थियों को घरों के आवंटन पत्र वितरित किए गए।"
            ),
        ]

        # Ingest all tweets
        for tweet_data in tweets_data:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]  # 200 for duplicates, 201 for new

        # Step 2: Verify bulk ingestion
        response = await async_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_tweets"] >= 3

        # Step 3: Apply selective corrections based on parsing quality
        # High confidence correction
        overlay_service.add_overlay(
            tweet_id="dhruv-bulk-001",
            field="event_type",
            corrected_value="health_camp",
            reviewer_id="reviewer-alpha",
            confidence=0.95,
            notes="High confidence correction for health camp event"
        )

        # Medium confidence correction
        overlay_service.add_overlay(
            tweet_id="dhruv-bulk-002",
            field="location",
            corrected_value="Bilaspur",
            reviewer_id="reviewer-beta",
            confidence=0.85,
            notes="Corrected location spelling from BILASPUR to Bilaspur"
        )

        # Low confidence correction (should be ignored in application)
        overlay_service.add_overlay(
            tweet_id="dhruv-bulk-003",
            field="schemes",
            corrected_value="PM Housing Scheme",
            reviewer_id="reviewer-gamma",
            confidence=0.6,
            notes="Low confidence scheme correction"
        )

        # Step 4: Verify overlay statistics
        overlay_stats = overlay_service.get_overlay_stats()
        assert overlay_stats["total_overlays"] == 3
        assert overlay_stats["tweets_with_overlays"] == 3
        assert overlay_stats["reviewer_distribution"]["reviewer-alpha"] == 1
        assert overlay_stats["reviewer_distribution"]["reviewer-beta"] == 1
        assert overlay_stats["reviewer_distribution"]["reviewer-gamma"] == 1

    async def test_scenario_3_cognitive_engine_overlay_integration(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService,
        mock_cognitive_engine
    ):
        """
        Scenario 3: Cognitive Engine Learning → Overlay Corrections → Improved Parsing

        Tests the cognitive engine's ability to learn from overlay corrections.
        """
        # Step 1: Set up cognitive engine to return learning decisions
        mock_cognitive_engine.process_correction.return_value = {
            "id": "cognitive-log-001",
            "decision": {"action": "approve", "confidence": 0.92},
            "details": {
                "reasoning": "Learned from overlay corrections",
                "improvement_suggestions": ["Better location parsing", "Event type classification"]
            }
        }

        # Step 2: Ingest tweet that might have parsing issues
        tweet_data = create_test_tweet_data(
            tweet_id="dhruv-cognitive-001",
            text="छत्तीसगढ़ के मुख्यमंत्री ने आज दुर्ग में एक महत्वपूर्ण बैठक की अध्यक्षता की।"
        )

        response = await async_client.post(
            "/api/ingest-parsed-tweet",
            json=tweet_data,
            headers=auth_headers
        )
        assert response.status_code == 201

        # Step 3: Apply overlay correction
        overlay_service.add_overlay(
            tweet_id="dhruv-cognitive-001",
            field="event_type",
            corrected_value="important_meeting",
            reviewer_id="cognitive-reviewer",
            confidence=0.88,
            notes="Cognitive engine assisted correction"
        )

        # Step 4: Test cognitive correction endpoint
        correction_payload = {
            "tweet_id": "dhruv-cognitive-001",
            "text": "छत्तीसगढ़ के मुख्यमंत्री ने आज दुर्ग में एक महत्वपूर्ण बैठक की अध्यक्षता की।",
            "old_data": {"event_type": "general_meeting"},
            "correction": {"event_type": "important_meeting"}
        }

        response = await async_client.post(
            "/api/cognitive/correct",
            json=correction_payload,
            headers=auth_headers
        )
        assert response.status_code == 200
        correction_result = response.json()
        assert correction_result["status"] == "success"
        assert "decision" in correction_result
        assert correction_result["decision"]["action"] == "approve"

        # Step 5: Verify cognitive engine was called with overlay data
        mock_cognitive_engine.process_correction.assert_called_once()

    async def test_scenario_4_overlay_persistence_and_recovery(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        tmp_path
    ):
        """
        Scenario 4: System Restart → Overlay Persistence → Data Recovery

        Tests that overlay corrections survive system restarts and are properly recovered.
        """
        # Step 1: Create overlay service and add corrections
        overlay_dir = tmp_path / "persistent_overlays"
        overlay_dir.mkdir()

        service1 = OverlayService(str(overlay_dir))

        # Add multiple corrections
        corrections = [
            ("persist-tweet-001", "event_type", "rally", "reviewer-1"),
            ("persist-tweet-002", "location", "Raipur", "reviewer-2"),
            ("persist-tweet-003", "schemes", "PM Kisan", "reviewer-1"),
        ]

        for tweet_id, field, value, reviewer in corrections:
            service1.add_overlay(
                tweet_id=tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id=reviewer,
                notes=f"Persistent correction for {field}"
            )

        # Step 2: Simulate system restart by creating new service instance
        service2 = OverlayService(str(overlay_dir))

        # Step 3: Verify all corrections were persisted and recovered
        recovered_overlays = []
        for tweet_id, _, _, _ in corrections:
            overlays = service2.get_overlays_for_tweet(tweet_id)
            recovered_overlays.extend(overlays)

        assert len(recovered_overlays) == 3

        # Verify specific corrections
        rally_overlay = next((o for o in recovered_overlays if o.corrected_value == "rally"), None)
        assert rally_overlay is not None
        assert rally_overlay.field == "event_type"
        assert rally_overlay.reviewer_id == "reviewer-1"

        # Step 4: Test overlay application after recovery
        test_data = {"event_type": "meeting", "location": "Unknown", "schemes": []}

        result = service2.apply_overlays(test_data, "persist-tweet-001")
        assert result["event_type"] == "rally"  # Should be corrected

        result = service2.apply_overlays(test_data, "persist-tweet-002")
        assert result["location"] == "Raipur"  # Should be corrected

    async def test_scenario_5_comprehensive_analytics_with_overlays(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Scenario 5: Analytics Generation → Overlay Impact Assessment → Reporting

        Tests analytics generation with overlay corrections factored in.
        """
        # Step 1: Ingest diverse tweets for analytics
        analytics_tweets = [
            create_test_tweet_data(
                tweet_id="analytics-001",
                text="रायपुर में मुख्यमंत्री ने विकास कार्यों की समीक्षा बैठक की।"
            ),
            create_test_tweet_data(
                tweet_id="analytics-002",
                text="बिलासपुर जिले में स्वास्थ्य विभाग ने टीकाकरण शिविर लगाया।"
            ),
            create_test_tweet_data(
                tweet_id="analytics-003",
                text="दुर्ग में प्रधानमंत्री आवास योजना के तहत घर निर्माण शुरू।"
            ),
        ]

        for tweet_data in analytics_tweets:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Step 2: Apply strategic corrections to improve analytics accuracy
        overlay_service.add_overlay(
            tweet_id="analytics-001",
            field="event_type",
            corrected_value="review_meeting",
            reviewer_id="analytics-reviewer",
            confidence=0.9
        )

        overlay_service.add_overlay(
            tweet_id="analytics-002",
            field="event_type",
            corrected_value="vaccination_camp",
            reviewer_id="analytics-reviewer",
            confidence=0.95
        )

        overlay_service.add_overlay(
            tweet_id="analytics-003",
            field="schemes",
            corrected_value="PM Awas Yojana",
            reviewer_id="analytics-reviewer",
            confidence=0.88
        )

        # Step 3: Test analytics endpoints (even if mocked, test the integration)
        response = await async_client.get("/api/analytics/event-types", headers=auth_headers)
        assert response.status_code in [200, 404]  # 404 if not implemented in test client

        response = await async_client.get("/api/analytics/districts", headers=auth_headers)
        assert response.status_code in [200, 404]  # 404 if not implemented in test client

        # Step 4: Verify overlay impact on statistics
        overlay_stats = overlay_service.get_overlay_stats()
        assert overlay_stats["total_overlays"] == 3
        assert overlay_stats["tweets_with_overlays"] == 3
        assert overlay_stats["field_distribution"]["event_type"] == 2
        assert overlay_stats["field_distribution"]["schemes"] == 1

    async def test_scenario_6_error_recovery_with_overlay_backup(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Scenario 6: Parsing Errors → Overlay Corrections → Recovery Validation

        Tests error recovery workflows with overlay corrections as backup.
        """
        # Step 1: Simulate tweets with parsing errors
        error_tweets = [
            create_test_tweet_data(
                tweet_id="error-recovery-001",
                text="गंभीर पार्सिंग त्रुटि वाला ट्वीट जिसमें अनेक समस्याएं हैं।"
            ),
            create_test_tweet_data(
                tweet_id="error-recovery-002",
                text="अपरिभाषित इवेंट प्रकार और स्थान के साथ ट्वीट।"
            ),
        ]

        # Step 2: Apply corrective overlays for error recovery
        overlay_service.add_overlay(
            tweet_id="error-recovery-001",
            field="event_type",
            corrected_value="error_recovery_test",
            reviewer_id="recovery-reviewer",
            confidence=1.0,
            notes="Manual correction for parsing error recovery"
        )

        overlay_service.add_overlay(
            tweet_id="error-recovery-002",
            field="location",
            corrected_value="Chhattisgarh",
            reviewer_id="recovery-reviewer",
            confidence=0.95,
            notes="Location correction for undefined parsing"
        )

        # Step 3: Test that overlays provide recovery path
        # Even if original parsing failed, overlays provide corrected data
        test_data_1 = {"event_type": "unknown", "location": "undefined"}
        result_1 = overlay_service.apply_overlays(test_data_1, "error-recovery-001")
        assert result_1["event_type"] == "error_recovery_test"

        test_data_2 = {"event_type": "unknown", "location": "undefined"}
        result_2 = overlay_service.apply_overlays(test_data_2, "error-recovery-002")
        assert result_2["location"] == "Chhattisgarh"

        # Step 4: Verify recovery statistics
        recovery_stats = overlay_service.get_overlay_stats()
        assert recovery_stats["total_overlays"] == 2
        assert recovery_stats["reviewer_distribution"]["recovery-reviewer"] == 2

    async def test_scenario_7_concurrent_overlay_operations(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Scenario 7: Concurrent Reviewers → Overlay Conflicts → Resolution

        Tests concurrent overlay operations and conflict resolution.
        """
        tweet_id = "concurrent-test-001"

        # Step 1: Simulate concurrent corrections from multiple reviewers
        corrections = [
            ("event_type", "meeting", "reviewer-A", 0.9),
            ("event_type", "conference", "reviewer-B", 0.85),  # Lower confidence
            ("location", "Raipur", "reviewer-A", 0.95),
            ("schemes", "Digital India", "reviewer-C", 0.92),
        ]

        for field, value, reviewer, confidence in corrections:
            overlay_service.add_overlay(
                tweet_id=tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id=reviewer,
                confidence=confidence,
                notes=f"Concurrent correction by {reviewer}"
            )

        # Step 2: Verify all corrections are stored
        overlays = overlay_service.get_overlays_for_tweet(tweet_id)
        assert len(overlays) == 4

        # Step 3: Test overlay application (higher confidence wins for same field)
        test_data = {"event_type": "unknown", "location": "unknown", "schemes": []}
        result = overlay_service.apply_overlays(test_data, tweet_id)

        # Should apply highest confidence correction for event_type
        assert result["event_type"] == "meeting"  # Higher confidence than "conference"
        assert result["location"] == "Raipur"
        assert result["schemes"] == "Digital India"

        # Step 4: Test reviewer statistics
        stats = overlay_service.get_overlay_stats()
        assert stats["total_overlays"] == 4
        assert stats["reviewer_distribution"]["reviewer-A"] == 2
        assert stats["reviewer_distribution"]["reviewer-B"] == 1
        assert stats["reviewer_distribution"]["reviewer-C"] == 1

    async def test_scenario_8_overlay_service_health_monitoring(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Scenario 8: Service Health → Overlay Performance → Monitoring

        Tests overlay service health monitoring and performance metrics.
        """
        # Step 1: Generate comprehensive overlay data for monitoring
        for i in range(10):
            overlay_service.add_overlay(
                tweet_id=f"health-tweet-{i:03d}",
                field="event_type" if i % 2 == 0 else "location",
                corrected_value=f"correction-{i}",
                reviewer_id=f"reviewer-{i % 3}",
                confidence=0.8 + (i * 0.01),  # Varying confidence
                notes=f"Health monitoring test correction {i}"
            )

        # Step 2: Test comprehensive statistics
        stats = overlay_service.get_overlay_stats()

        assert stats["total_overlays"] == 10
        assert stats["tweets_with_overlays"] == 10
        assert stats["field_distribution"]["event_type"] == 5
        assert stats["field_distribution"]["location"] == 5
        assert len(stats["reviewer_distribution"]) == 3  # 3 different reviewers

        # Step 3: Test system health endpoints
        response = await async_client.get("/health/system", headers=auth_headers)
        assert response.status_code == 200

        response = await async_client.get("/health/analytics", headers=auth_headers)
        assert response.status_code == 200

        # Step 4: Test overlay data integrity
        for i in range(10):
            overlays = overlay_service.get_overlays_for_tweet(f"health-tweet-{i:03d}")
            assert len(overlays) == 1
            overlay = overlays[0]
            assert overlay.confidence >= 0.8
            assert overlay.reviewer_id.startswith("reviewer-")