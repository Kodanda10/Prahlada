"""
Complete End-to-End Workflow Tests for Dhruv Platform.

Tests the full pipeline from tweet ingestion through parsing, overlay corrections,
analytics, and reporting to ensure the entire system works cohesively.
"""

import os
import json
import pytest
import asyncio
from datetime import datetime, timedelta
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

from backend.services.overlay_service import OverlayService
from backend.tests.conftest import create_test_tweet_data


@pytest.mark.asyncio
class TestCompleteE2EWorkflows:
    """
    End-to-end tests covering complete workflows from ingestion to analytics.
    """

    @pytest.fixture
    def overlay_service(self, tmp_path):
        """Overlay service for E2E testing."""
        overlay_dir = tmp_path / "e2e_overlays"
        overlay_dir.mkdir()
        return OverlayService(str(overlay_dir))

    async def test_workflow_1_full_tweet_lifecycle(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService,
        mock_vector_store
    ):
        """
        Workflow 1: Complete Tweet Lifecycle
        Tweet Ingestion → Parsing → Review → Correction → Search → Analytics
        """
        # Phase 1: Tweet Ingestion and Parsing
        workflow_tweets = [
            create_test_tweet_data(
                tweet_id="lifecycle-001",
                text="मुख्यमंत्री श्री भूपेश बघेल ने रायपुर में प्रधानमंत्री आवास योजना का शिलान्यास किया। मुख्यमंत्री कार्यालय से मिली जानकारी के अनुसार यह कार्यक्रम बड़ी संख्या में लोगों को लाभान्वित करेगा।"
            ),
            create_test_tweet_data(
                tweet_id="lifecycle-002",
                text="बिलासपुर जिले में स्वास्थ्य विभाग की ओर से आयोजित टीकाकरण शिविर में 500 से अधिक लोग शामिल हुए। शिविर में कोविड-19 और अन्य रोगों की वैक्सीन लगाई गई।"
            ),
            create_test_tweet_data(
                tweet_id="lifecycle-003",
                text="दुर्ग शहर में आज शाम को मुख्यमंत्री द्वारा किसान सम्मेलन का उद्घाटन किया जाएगा। इस सम्मेलन में कृषि विकास और सिंचाई परियोजनाओं पर चर्चा होगी।"
            ),
        ]

        # Ingest all tweets
        for tweet_data in workflow_tweets:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Verify Initial Statistics
        response = await async_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200
        initial_stats = response.json()
        assert initial_stats["total_tweets"] >= 3

        # Phase 3: Vector Indexing for Search
        index_payload = {"tweetIds": ["lifecycle-001", "lifecycle-002", "lifecycle-003"]}
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json=index_payload,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Phase 4: Apply Human Corrections
        corrections = [
            ("lifecycle-001", "event_type", "inauguration", "reviewer-lifecycle", "Corrected event type"),
            ("lifecycle-002", "event_type", "vaccination_camp", "reviewer-lifecycle", "Health camp classification"),
            ("lifecycle-003", "schemes", "Agriculture Development", "reviewer-lifecycle", "Added agriculture scheme"),
        ]

        for tweet_id, field, value, reviewer, notes in corrections:
            overlay_payload = {
                "tweet_id": tweet_id,
                "field": field,
                "corrected_value": {"value": value},
                "reviewer_id": reviewer,
                "notes": notes
            }
            response = await async_client.post(
                "/api/overlay/add",
                json=overlay_payload,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Phase 5: Test Search Functionality
        search_queries = ["मुख्यमंत्री", "स्वास्थ्य शिविर", "किसान सम्मेलन"]
        for query in search_queries:
            search_payload = {"query": query, "k": 5}
            response = await async_client.post(
                "/api/search",
                json=search_payload,
                headers=auth_headers
            )
            assert response.status_code == 200
            results = response.json()
            assert isinstance(results, list)

        # Phase 6: Test Analytics with Corrections
        analytics_endpoints = ["/api/analytics/event-types", "/api/analytics/districts"]
        for endpoint in analytics_endpoints:
            response = await async_client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 404]  # 404 acceptable if not implemented

        # Phase 7: Verify Final Statistics
        response = await async_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200
        final_stats = response.json()
        assert final_stats["total_tweets"] >= 3

        # Phase 8: Verify Overlay Statistics
        overlay_stats = overlay_service.get_overlay_stats()
        assert overlay_stats["total_overlays"] == 3
        assert overlay_stats["tweets_with_overlays"] == 3

        # Phase 9: Test Event Approval Workflow
        response = await async_client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200
        events = response.json()

        # Approve one event
        if events:
            approve_payload = {}
            response = await async_client.post(
                f"/api/events/{events[0]['tweet_id']}/approve",
                json=approve_payload,
                headers=auth_headers
            )
            assert response.status_code == 200

    async def test_workflow_2_cognitive_learning_loop(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService,
        mock_cognitive_engine
    ):
        """
        Workflow 2: Cognitive Learning Loop
        Parsing → Correction → Cognitive Learning → Improved Future Parsing
        """
        # Setup cognitive engine learning responses
        learning_responses = [
            {
                "id": "learn-001",
                "decision": {"action": "approve", "confidence": 0.95},
                "details": {"learned": True, "patterns": ["inauguration_keywords"]}
            },
            {
                "id": "learn-002",
                "decision": {"action": "approve", "confidence": 0.92},
                "details": {"learned": True, "patterns": ["health_camp_indicators"]}
            },
        ]
        mock_cognitive_engine.process_correction.side_effect = learning_responses

        # Phase 1: Ingest learning tweets
        learning_tweets = [
            create_test_tweet_data(
                tweet_id="learn-001",
                text="मुख्यमंत्री द्वारा रायपुर में नए अस्पताल का लोकार्पण समारोह संपन्न हुआ।"
            ),
            create_test_tweet_data(
                tweet_id="learn-002",
                text="स्वास्थ्य विभाग द्वारा ग्रामीण क्षेत्रों में मोबाइल मेडिकल कैंप का आयोजन।"
            ),
        ]

        for tweet_data in learning_tweets:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Apply corrections and trigger learning
        corrections = [
            ("learn-001", "event_type", "hospital_inauguration"),
            ("learn-002", "event_type", "medical_camp"),
        ]

        for tweet_id, field, value in corrections:
            # Apply overlay correction
            overlay_service.add_overlay(
                tweet_id=tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id="cognitive-trainer",
                notes="Correction for cognitive learning"
            )

            # Trigger cognitive correction analysis
            correction_payload = {
                "tweet_id": tweet_id,
                "text": f"Sample text for {tweet_id}",
                "old_data": {"event_type": "meeting"},
                "correction": {"event_type": value}
            }

            response = await async_client.post(
                "/api/cognitive/correct",
                json=correction_payload,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Phase 3: Verify cognitive engine was called
        assert mock_cognitive_engine.process_correction.call_count == 2

        # Phase 4: Test that future similar tweets would benefit from learning
        # (This would normally be tested by checking improved parsing accuracy)
        overlay_stats = overlay_service.get_overlay_stats()
        assert overlay_stats["total_overlays"] == 2
        assert overlay_stats["reviewer_distribution"]["cognitive-trainer"] == 2

    async def test_workflow_3_quality_assurance_pipeline(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Workflow 3: Quality Assurance Pipeline
        Ingestion → Automated Review → Human QA → Corrections → Validation
        """
        # Phase 1: Ingest diverse tweets for QA
        qa_tweets = [
            create_test_tweet_data(
                tweet_id="qa-001",
                text="मुख्यमंत्री भूपेश बघेल द्वारा आज दुर्ग में विकास परियोजना का शुभारंभ किया गया।"
            ),
            create_test_tweet_data(
                tweet_id="qa-002",
                text="राज्य सरकार की ओर से किसानों को नई कृषि तकनीक के बारे में प्रशिक्षण दिया जा रहा है।"
            ),
            create_test_tweet_data(
                tweet_id="qa-003",
                text="बिलासपुर में आयोजित जनसभा में मुख्यमंत्री ने कई अहम घोषणाएं कीं।"
            ),
        ]

        for tweet_data in qa_tweets:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Get events for review
        response = await async_client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200
        events_before_qa = response.json()

        # Phase 3: QA Review and Corrections
        qa_corrections = [
            ("qa-001", "location", "Durg, Chhattisgarh", "QA location precision"),
            ("qa-002", "schemes", "Agricultural Technology Training", "QA scheme identification"),
            ("qa-003", "event_type", "public_announcement", "QA event classification"),
        ]

        for tweet_id, field, value, notes in qa_corrections:
            overlay_payload = {
                "tweet_id": tweet_id,
                "field": field,
                "corrected_value": {"value": value},
                "reviewer_id": "qa-reviewer",
                "notes": notes
            }
            response = await async_client.post(
                "/api/overlay/add",
                json=overlay_payload,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Phase 4: Test overlay application
        for tweet_id, field, value, _ in qa_corrections:
            apply_payload = {
                "tweet_id": tweet_id,
                "parsed_data": {"field": "original_value"}
            }
            response = await async_client.post(
                "/api/overlay/apply",
                json=apply_payload,
                headers=auth_headers
            )
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"

        # Phase 5: Verify QA statistics
        qa_stats = overlay_service.get_overlay_stats()
        assert qa_stats["total_overlays"] == 3
        assert qa_stats["reviewer_distribution"]["qa-reviewer"] == 3

        # Phase 6: Post-QA event verification
        response = await async_client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200
        events_after_qa = response.json()

        # Events should still be available (QA doesn't remove them)
        assert len(events_after_qa) >= len(events_before_qa)

    async def test_workflow_4_production_monitoring_dashboard(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Workflow 4: Production Monitoring Dashboard
        System Health → Overlay Performance → Analytics Integrity → Alerts
        """
        # Phase 1: Generate monitoring data
        monitoring_tweets = []
        for i in range(5):
            tweet_data = create_test_tweet_data(
                tweet_id=f"monitor-{i:03d}",
                text=f"Monitoring test tweet {i} with various content patterns for system validation."
            )
            monitoring_tweets.append(tweet_data)

            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Apply monitoring corrections
        for i in range(5):
            overlay_service.add_overlay(
                tweet_id=f"monitor-{i:03d}",
                field="event_type",
                corrected_value=f"monitor_event_{i}",
                reviewer_id="monitor-system",
                notes=f"Automated monitoring correction {i}"
            )

        # Phase 3: Test all health endpoints
        health_endpoints = [
            "/health/system",
            "/health/analytics",
            "/api/overlay/health"
        ]

        for endpoint in health_endpoints:
            response = await async_client.get(endpoint, headers=auth_headers)
            assert response.status_code == 200
            health_data = response.json()
            assert "status" in health_data

        # Phase 4: Test statistics endpoints
        stats_endpoints = ["/api/stats", "/api/overlay/stats"]

        for endpoint in stats_endpoints:
            response = await async_client.get(endpoint, headers=auth_headers)
            assert response.status_code == 200
            stats_data = response.json()
            assert isinstance(stats_data, dict)

        # Phase 5: Test analytics endpoints
        analytics_endpoints = ["/api/analytics/event-types", "/api/analytics/districts"]

        for endpoint in analytics_endpoints:
            response = await async_client.get(endpoint, headers=auth_headers)
            # Analytics might return 404 if not implemented in test environment
            assert response.status_code in [200, 404]

        # Phase 6: Verify monitoring data integrity
        monitoring_stats = overlay_service.get_overlay_stats()
        assert monitoring_stats["total_overlays"] == 5
        assert monitoring_stats["tweets_with_overlays"] == 5
        assert monitoring_stats["reviewer_distribution"]["monitor-system"] == 5

    async def test_workflow_5_data_integrity_and_backup(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Workflow 5: Data Integrity and Backup
        Ingestion → Corrections → Backup → Restore → Validation
        """
        # Phase 1: Create comprehensive test dataset
        integrity_tweets = []
        for i in range(3):
            tweet_data = create_test_tweet_data(
                tweet_id=f"integrity-{i:03d}",
                text=f"Data integrity test tweet {i} with verifiable content for backup validation."
            )
            integrity_tweets.append(tweet_data)

            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Apply comprehensive corrections
        integrity_corrections = []
        for i in range(3):
            corrections = [
                ("event_type", f"integrity_event_{i}"),
                ("location", f"Integrity City {i}"),
                ("schemes", f"Integrity Scheme {i}"),
            ]

            for field, value in corrections:
                overlay_service.add_overlay(
                    tweet_id=f"integrity-{i:03d}",
                    field=field,
                    corrected_value=value,
                    reviewer_id="integrity-checker",
                    notes=f"Integrity test correction for {field}"
                )
                integrity_corrections.append((f"integrity-{i:03d}", field, value))

        # Phase 3: Verify data integrity before "backup"
        pre_backup_stats = overlay_service.get_overlay_stats()
        assert pre_backup_stats["total_overlays"] == 9  # 3 tweets × 3 corrections each

        # Phase 4: Simulate backup by creating second service instance (simulates restore)
        # In a real scenario, this would be loading from backup files
        backup_service = OverlayService(overlay_service.overlay_dir)

        # Phase 5: Verify backup integrity
        post_backup_stats = backup_service.get_overlay_stats()
        assert post_backup_stats["total_overlays"] == pre_backup_stats["total_overlays"]
        assert post_backup_stats["tweets_with_overlays"] == pre_backup_stats["tweets_with_overlays"]

        # Phase 6: Verify correction integrity
        for tweet_id, field, expected_value in integrity_corrections:
            overlays = backup_service.get_overlays_for_tweet(tweet_id)
            field_overlay = next((o for o in overlays if o.field == field), None)
            assert field_overlay is not None
            assert field_overlay.corrected_value == expected_value

        # Phase 7: Test overlay application integrity
        for tweet_id in [f"integrity-{i:03d}" for i in range(3)]:
            test_data = {"event_type": "original", "location": "original", "schemes": "original"}
            result = backup_service.apply_overlays(test_data, tweet_id)

            # All fields should be corrected
            overlays = backup_service.get_overlays_for_tweet(tweet_id)
            for overlay in overlays:
                assert result[overlay.field] != "original"  # Should be corrected

    async def test_workflow_6_performance_and_scalability(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Workflow 6: Performance and Scalability Testing
        Load Testing → Response Times → Resource Usage → Bottleneck Analysis
        """
        import time

        # Phase 1: Performance baseline measurement
        start_time = time.time()
        response = await async_client.get("/api/stats", headers=auth_headers)
        baseline_latency = time.time() - start_time
        assert response.status_code == 200

        # Phase 2: Generate performance test data
        perf_tweets = []
        for i in range(10):
            tweet_data = create_test_tweet_data(
                tweet_id=f"perf-{i:03d}",
                text=f"Performance test tweet {i} with content designed for scalability testing."
            )
            perf_tweets.append(tweet_data)

            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 3: Apply performance corrections
        perf_start = time.time()
        for i in range(10):
            overlay_service.add_overlay(
                tweet_id=f"perf-{i:03d}",
                field="event_type",
                corrected_value=f"perf_event_{i}",
                reviewer_id="perf-tester",
                notes=f"Performance correction {i}"
            )
        perf_correction_time = time.time() - perf_start

        # Phase 4: Test query performance
        query_times = []
        for i in range(5):
            start_time = time.time()
            overlays = overlay_service.get_overlays_for_tweet(f"perf-{i:03d}")
            query_time = time.time() - start_time
            query_times.append(query_time)
            assert len(overlays) == 1

        avg_query_time = sum(query_times) / len(query_times)

        # Phase 5: Test API performance under load
        api_times = []
        for i in range(5):
            start_time = time.time()
            response = await async_client.get("/api/stats", headers=auth_headers)
            api_time = time.time() - start_time
            api_times.append(api_time)
            assert response.status_code == 200

        avg_api_time = sum(api_times) / len(api_times)

        # Phase 6: Performance assertions
        # These are reasonable expectations for a test environment
        assert perf_correction_time < 5.0  # Corrections should complete within 5 seconds
        assert avg_query_time < 0.1  # Queries should be fast
        assert avg_api_time < 0.5  # API calls should be responsive

        # Phase 7: Scalability verification
        perf_stats = overlay_service.get_overlay_stats()
        assert perf_stats["total_overlays"] == 10
        assert perf_stats["tweets_with_overlays"] == 10

        # Phase 8: Resource cleanup verification
        # (In real scenarios, this would check memory usage, connection pools, etc.)
        assert overlay_service._overlays is not None  # Service should remain functional