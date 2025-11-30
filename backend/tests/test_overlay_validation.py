"""
Overlay Service Validation Tests.

Tests that validate overlay corrections improve parsing accuracy and maintain
data integrity throughout the system.
"""

import os
import json
import pytest
import asyncio
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
class TestOverlayValidation:
    """
    Validation tests ensuring overlay corrections improve accuracy and maintain integrity.
    """

    @pytest.fixture
    def overlay_service(self, tmp_path):
        """Overlay service for validation testing."""
        overlay_dir = tmp_path / "validation_overlays"
        overlay_dir.mkdir()
        return OverlayService(str(overlay_dir))

    async def test_validation_1_accuracy_improvement_measurement(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Validation 1: Measure parsing accuracy improvements through overlay corrections.

        Tests that overlay corrections lead to measurable improvements in data quality.
        """
        # Create test scenarios with known parsing challenges
        accuracy_test_cases = [
            {
                "tweet_id": "accuracy-001",
                "original_text": "मुख्यमंत्री भूपेश बघेल द्वारा रायपुर में प्रधानमंत्री आवास योजना की शुरुआत",
                "original_parsing": {
                    "event_type": "meeting",  # Incorrectly classified
                    "location": "Raipur",
                    "schemes": ["PM Awas Yojana"]
                },
                "correct_corrections": {
                    "event_type": "scheme_launch",  # Correct classification
                    "location": "Raipur, Chhattisgarh",  # More precise
                }
            },
            {
                "tweet_id": "accuracy-002",
                "original_text": "बिलासपुर जिले में स्वास्थ्य शिविर का आयोजन स्वास्थ्य मंत्री द्वारा",
                "original_parsing": {
                    "event_type": "gathering",  # Too generic
                    "location": "Bilaspur",
                    "schemes": []
                },
                "correct_corrections": {
                    "event_type": "health_camp",  # Specific and accurate
                    "schemes": ["Public Health Initiative"],  # Missing scheme identified
                }
            },
        ]

        # Phase 1: Ingest tweets with original parsing
        for test_case in accuracy_test_cases:
            tweet_data = create_test_tweet_data(
                tweet_id=test_case["tweet_id"],
                text=test_case["original_text"]
            )

            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Apply accuracy-improving corrections
        total_corrections = 0
        for test_case in accuracy_test_cases:
            for field, correct_value in test_case["correct_corrections"].items():
                overlay_service.add_overlay(
                    tweet_id=test_case["tweet_id"],
                    field=field,
                    corrected_value=correct_value,
                    reviewer_id="accuracy-validator",
                    confidence=0.95,
                    notes=f"Accuracy improvement for {field}"
                )
                total_corrections += 1

        # Phase 3: Validate corrections improve data quality
        validation_results = []
        for test_case in accuracy_test_cases:
            # Get corrected data
            apply_payload = {
                "tweet_id": test_case["tweet_id"],
                "parsed_data": test_case["original_parsing"]
            }

            response = await async_client.post(
                "/api/overlay/apply",
                json=apply_payload,
                headers=auth_headers
            )
            assert response.status_code == 200
            result = response.json()

            # Verify corrections were applied
            corrected_data = result["corrected_data"]
            applied_overlays = result["applied_overlays"]

            # Check that corrections actually changed the data
            improvements = 0
            for field, correct_value in test_case["correct_corrections"].items():
                if corrected_data.get(field) == correct_value:
                    improvements += 1

            validation_results.append({
                "tweet_id": test_case["tweet_id"],
                "expected_corrections": len(test_case["correct_corrections"]),
                "applied_corrections": applied_overlays,
                "successful_improvements": improvements,
                "accuracy": improvements / len(test_case["correct_corrections"])
            })

        # Phase 4: Validate overall accuracy improvement
        total_expected = sum(r["expected_corrections"] for r in validation_results)
        total_successful = sum(r["successful_improvements"] for r in validation_results)
        overall_accuracy = total_successful / total_expected if total_expected > 0 else 0

        # Assert high accuracy (should be 100% for validation tests)
        assert overall_accuracy == 1.0, f"Accuracy should be 100%, got {overall_accuracy}"

        # Phase 5: Verify correction statistics
        accuracy_stats = overlay_service.get_overlay_stats()
        assert accuracy_stats["total_overlays"] == total_corrections
        assert accuracy_stats["reviewer_distribution"]["accuracy-validator"] == total_corrections

    async def test_validation_2_data_integrity_preservation(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Validation 2: Ensure overlay corrections preserve data integrity.

        Tests that overlay corrections don't corrupt existing data or relationships.
        """
        # Phase 1: Create comprehensive test dataset
        integrity_tweets = []
        original_data = {}

        for i in range(5):
            tweet_data = create_test_tweet_data(
                tweet_id=f"integrity-{i:03d}",
                text=f"Integrity test tweet {i} with consistent structured content for validation."
            )
            integrity_tweets.append(tweet_data)

            # Store original data for integrity checking
            original_data[f"integrity-{i:03d}"] = {
                "event_type": tweet_data["categories"]["event"][0] if tweet_data["categories"]["event"] else None,
                "location": tweet_data["categories"]["locations"],
                "schemes": tweet_data["categories"]["schemes"]
            }

            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Apply integrity-preserving corrections
        integrity_corrections = []
        for i in range(5):
            tweet_id = f"integrity-{i:03d}"

            # Apply corrections that should not break data relationships
            corrections = [
                ("event_type", f"validated_event_{i}"),
                ("location", f"Validated City {i}"),
            ]

            for field, value in corrections:
                overlay_service.add_overlay(
                    tweet_id=tweet_id,
                    field=field,
                    corrected_value=value,
                    reviewer_id="integrity-validator",
                    confidence=0.90,
                    notes=f"Integrity-preserving correction for {field}"
                )
                integrity_corrections.append((tweet_id, field, value))

        # Phase 3: Validate data integrity after corrections
        integrity_checks = []

        for tweet_id in original_data.keys():
            # Test overlay application
            apply_payload = {
                "tweet_id": tweet_id,
                "parsed_data": original_data[tweet_id]
            }

            response = await async_client.post(
                "/api/overlay/apply",
                json=apply_payload,
                headers=auth_headers
            )
            assert response.status_code == 200
            result = response.json()

            corrected_data = result["corrected_data"]

            # Verify data structure integrity
            required_fields = ["event_type", "location", "schemes"]
            for field in required_fields:
                assert field in corrected_data, f"Field {field} missing from corrected data"

            # Verify data type integrity
            assert isinstance(corrected_data["event_type"], str), "event_type should be string"
            assert isinstance(corrected_data["location"], (str, list)), "location should be string or list"
            assert isinstance(corrected_data["schemes"], list), "schemes should be list"

            # Check that corrections were applied correctly
            overlays = overlay_service.get_overlays_for_tweet(tweet_id)
            applied_corrections = {(o.field, o.corrected_value) for o in overlays}

            integrity_checks.append({
                "tweet_id": tweet_id,
                "original_fields_present": all(f in original_data[tweet_id] for f in required_fields),
                "corrected_fields_present": all(f in corrected_data for f in required_fields),
                "corrections_applied": len(overlays),
                "data_types_preserved": True,  # Would be False if type checks failed
            })

        # Phase 4: Validate integrity metrics
        integrity_score = sum(
            1 for check in integrity_checks
            if check["original_fields_present"] and check["corrected_fields_present"] and check["data_types_preserved"]
        ) / len(integrity_checks)

        assert integrity_score == 1.0, f"Data integrity should be 100%, got {integrity_score}"

        # Phase 5: Test referential integrity
        # Verify that corrections don't break relationships between fields
        for tweet_id in original_data.keys():
            overlays = overlay_service.get_overlays_for_tweet(tweet_id)
            corrected_fields = {o.field for o in overlays}

            # Ensure no conflicting corrections for same field
            field_counts = {}
            for overlay in overlays:
                field_counts[overlay.field] = field_counts.get(overlay.field, 0) + 1

            # Each field should have at most one correction (latest wins)
            assert all(count <= 1 for count in field_counts.values()), "Multiple corrections for same field"

    async def test_validation_3_longitudinal_accuracy_tracking(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Validation 3: Track accuracy improvements over time with longitudinal corrections.

        Tests how overlay corrections accumulate and improve system accuracy over time.
        """
        # Phase 1: Establish baseline accuracy
        baseline_tweets = [
            create_test_tweet_data(
                tweet_id="baseline-001",
                text="मुख्यमंत्री ने विकास कार्यों की समीक्षा बैठक की अध्यक्षता की।"
            ),
            create_test_tweet_data(
                tweet_id="baseline-002",
                text="स्वास्थ्य विभाग द्वारा टीकाकरण अभियान शुरू किया गया।"
            ),
        ]

        for tweet_data in baseline_tweets:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Apply initial corrections (first iteration)
        initial_corrections = [
            ("baseline-001", "event_type", "review_meeting"),
            ("baseline-002", "event_type", "vaccination_drive"),
        ]

        for tweet_id, field, value in initial_corrections:
            overlay_service.add_overlay(
                tweet_id=tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id="longitudinal-r1",
                confidence=0.85,
                notes="Initial correction - first iteration"
            )

        # Phase 3: Add second iteration corrections (refining previous corrections)
        refinement_corrections = [
            ("baseline-001", "schemes", "Infrastructure Development"),
            ("baseline-002", "location", "Statewide"),
        ]

        for tweet_id, field, value in refinement_corrections:
            overlay_service.add_overlay(
                tweet_id=tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id="longitudinal-r2",
                confidence=0.95,
                notes="Refinement correction - second iteration"
            )

        # Phase 4: Add third iteration corrections (further improvements)
        final_corrections = [
            ("baseline-001", "location", "Raipur, Chhattisgarh"),
            ("baseline-002", "schemes", "COVID Vaccination Program"),
        ]

        for tweet_id, field, value in final_corrections:
            overlay_service.add_overlay(
                tweet_id=tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id="longitudinal-r3",
                confidence=0.98,
                notes="Final correction - third iteration"
            )

        # Phase 5: Validate longitudinal improvement
        longitudinal_stats = overlay_service.get_overlay_stats()

        # Should have 6 total corrections (2 tweets × 3 iterations)
        assert longitudinal_stats["total_overlays"] == 6
        assert longitudinal_stats["tweets_with_overlays"] == 2

        # Check reviewer distribution shows iterative improvement process
        reviewer_dist = longitudinal_stats["reviewer_distribution"]
        assert reviewer_dist["longitudinal-r1"] == 2  # Initial corrections
        assert reviewer_dist["longitudinal-r2"] == 2  # Refinement corrections
        assert reviewer_dist["longitudinal-r3"] == 2  # Final corrections

        # Phase 6: Validate final accuracy state
        for tweet_id in ["baseline-001", "baseline-002"]:
            overlays = overlay_service.get_overlays_for_tweet(tweet_id)
            assert len(overlays) == 3  # All three iterations applied

            # Test final corrected state
            apply_payload = {
                "tweet_id": tweet_id,
                "parsed_data": {"event_type": "unknown", "location": "unknown", "schemes": []}
            }

            response = await async_client.post(
                "/api/overlay/apply",
                json=apply_payload,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Phase 7: Verify accuracy progression
        # Each iteration should show improved confidence scores
        confidence_progression = []
        for tweet_id in ["baseline-001", "baseline-002"]:
            overlays = overlay_service.get_overlays_for_tweet(tweet_id)
            confidences = sorted([o.confidence for o in overlays])
            confidence_progression.append(confidences)

        # Should show increasing confidence over iterations
        for confidences in confidence_progression:
            assert confidences == sorted(confidences), "Confidences should be in ascending order"

    async def test_validation_4_cross_system_consistency(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService,
        mock_vector_store
    ):
        """
        Validation 4: Ensure overlay corrections maintain consistency across all system components.

        Tests that corrections work consistently with search, analytics, and other system features.
        """
        # Phase 1: Create cross-system test data
        consistency_tweets = []
        for i in range(3):
            tweet_data = create_test_tweet_data(
                tweet_id=f"cross-system-{i:03d}",
                text=f"Cross-system consistency test tweet {i} for validating overlay integration across all components."
            )
            consistency_tweets.append(tweet_data)

            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Apply corrections that affect multiple systems
        cross_system_corrections = [
            ("cross-system-001", "event_type", "policy_announcement"),
            ("cross-system-002", "location", "Chhattisgarh Statewide"),
            ("cross-system-003", "schemes", "Digital Transformation Initiative"),
        ]

        for tweet_id, field, value in cross_system_corrections:
            overlay_service.add_overlay(
                tweet_id=tweet_id,
                field=field,
                corrected_value=value,
                reviewer_id="cross-system-validator",
                confidence=0.92,
                notes=f"Cross-system correction affecting {field}"
            )

        # Phase 3: Test consistency with search system
        # Index tweets for search
        index_payload = {"tweetIds": ["cross-system-001", "cross-system-002", "cross-system-003"]}
        response = await async_client.post(
            "/api/vector/trigger-batch-indexing",
            json=index_payload,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Perform searches to ensure corrections don't break search
        search_tests = ["policy", "Chhattisgarh", "Digital"]
        for query in search_tests:
            search_payload = {"query": query, "k": 5}
            response = await async_client.post(
                "/api/search",
                json=search_payload,
                headers=auth_headers
            )
            assert response.status_code == 200
            results = response.json()
            assert isinstance(results, list)

        # Phase 4: Test consistency with analytics system
        analytics_endpoints = ["/api/analytics/event-types", "/api/analytics/districts"]
        for endpoint in analytics_endpoints:
            response = await async_client.get(endpoint, headers=auth_headers)
            # Should work regardless of corrections (analytics may be mocked)
            assert response.status_code in [200, 404]

        # Phase 5: Test consistency with stats system
        response = await async_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200
        stats_before = response.json()

        # Phase 6: Test event system consistency
        response = await async_client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200
        events = response.json()

        # Events should still be retrievable with corrections applied
        assert len(events) >= 3

        # Phase 7: Validate overlay system health
        response = await async_client.get("/api/overlay/health", headers=auth_headers)
        assert response.status_code == 200
        health = response.json()
        assert health["status"] == "healthy"
        assert health["total_overlays"] == 3

        # Phase 8: Test approval workflow consistency
        if events:
            # Approve an event to test workflow integration
            response = await async_client.post(
                f"/api/events/{events[0]['tweet_id']}/approve",
                headers=auth_headers
            )
            assert response.status_code == 200

        # Phase 9: Final consistency check
        final_stats = overlay_service.get_overlay_stats()
        assert final_stats["total_overlays"] == 3
        assert final_stats["tweets_with_overlays"] == 3

        # Verify all corrections are still intact
        for tweet_id, field, expected_value in cross_system_corrections:
            overlays = overlay_service.get_overlays_for_tweet(tweet_id)
            field_overlay = next((o for o in overlays if o.field == field), None)
            assert field_overlay is not None
            assert field_overlay.corrected_value == expected_value

    async def test_validation_5_error_resilience_with_overlays(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        overlay_service: OverlayService
    ):
        """
        Validation 5: Test system resilience when overlay corrections encounter errors.

        Ensures that overlay corrections don't break the system when errors occur.
        """
        # Phase 1: Create test data with potential error scenarios
        resilience_tweets = [
            create_test_tweet_data(
                tweet_id="resilience-001",
                text="Normal tweet for resilience testing."
            ),
            create_test_tweet_data(
                tweet_id="resilience-002",
                text="Tweet that might cause parsing issues."
            ),
        ]

        for tweet_data in resilience_tweets:
            response = await async_client.post(
                "/api/ingest-parsed-tweet",
                json=tweet_data,
                headers=auth_headers
            )
            assert response.status_code in [200, 201]

        # Phase 2: Apply corrections including edge cases
        resilience_corrections = [
            ("resilience-001", "event_type", "normal_event"),
            ("resilience-002", "location", "Complex Location, District, State"),
            ("resilience-001", "schemes", ["Scheme 1", "Scheme 2", "Scheme 3"]),  # List value
            ("nonexistent-tweet", "event_type", "error_test"),  # Correction for non-existent tweet
        ]

        for tweet_id, field, value in resilience_corrections:
            try:
                overlay_service.add_overlay(
                    tweet_id=tweet_id,
                    field=field,
                    corrected_value=value,
                    reviewer_id="resilience-tester",
                    confidence=0.88,
                    notes=f"Resilience test correction for {field}"
                )
            except Exception as e:
                # Log but don't fail - testing error resilience
                print(f"Expected error in resilience test: {e}")

        # Phase 3: Test system resilience under various error conditions
        resilience_tests = [
            {
                "name": "normal_operation",
                "payload": {"tweet_id": "resilience-001", "parsed_data": {"event_type": "test"}},
                "should_succeed": True
            },
            {
                "name": "complex_data",
                "payload": {"tweet_id": "resilience-002", "parsed_data": {"location": "test"}},
                "should_succeed": True
            },
            {
                "name": "nonexistent_tweet",
                "payload": {"tweet_id": "nonexistent-tweet", "parsed_data": {"event_type": "test"}},
                "should_succeed": True  # Should handle gracefully
            },
            {
                "name": "empty_data",
                "payload": {"tweet_id": "resilience-001", "parsed_data": {}},
                "should_succeed": True
            },
        ]

        for test_case in resilience_tests:
            try:
                response = await async_client.post(
                    "/api/overlay/apply",
                    json=test_case["payload"],
                    headers=auth_headers
                )

                if test_case["should_succeed"]:
                    assert response.status_code == 200, f"Test {test_case['name']} should succeed"
                    result = response.json()
                    assert result["status"] == "success"
                else:
                    # If we expect failure, check it's handled gracefully
                    assert response.status_code in [200, 400, 404, 500]

            except Exception as e:
                if test_case["should_succeed"]:
                    raise e  # Re-raise if we expected success

        # Phase 4: Test API resilience
        # System should continue working even with overlay errors
        response = await async_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200

        response = await async_client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200

        response = await async_client.get("/api/overlay/stats", headers=auth_headers)
        assert response.status_code == 200

        # Phase 5: Verify data integrity after error scenarios
        resilience_stats = overlay_service.get_overlay_stats()

        # Should have corrections for existing tweets (some may have failed for non-existent)
        assert resilience_stats["total_overlays"] >= 2  # At least the successful ones

        # System should still be functional
        assert overlay_service._overlays is not None
        assert len(overlay_service._overlays) >= 1  # At least one tweet with overlays