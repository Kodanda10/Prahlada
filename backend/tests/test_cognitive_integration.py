"""
Integration tests for cognitive components.

Tests Phi 3.5 adapter and cognitive interface functionality.
"""

import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from backend.cognitive.phi_adapter import PhiAdapter, PhiSuggestions
from backend.cognitive.interface import CognitiveInterface


class TestPhiSuggestions:
    """Unit tests for PhiSuggestions data structure."""

    def test_phi_suggestions_creation(self):
        """Should create PhiSuggestions with default values."""
        suggestions = PhiSuggestions()

        assert suggestions.event_type_suggestions == []
        assert suggestions.location_candidates == []
        assert suggestions.scheme_suggestions == []
        assert suggestions.confidence_score == 0.0
        assert suggestions.reasoning == ""
        assert suggestions.raw_response is None

    def test_phi_suggestions_with_data(self):
        """Should create PhiSuggestions with provided data."""
        suggestions = PhiSuggestions(
            event_type_suggestions=["rally", "protest"],
            location_candidates=[{"name": "Delhi", "confidence": 0.9}],
            scheme_suggestions=["PM-KISAN"],
            confidence_score=0.85,
            reasoning="High confidence based on context",
            raw_response="raw json response"
        )

        assert suggestions.event_type_suggestions == ["rally", "protest"]
        assert suggestions.location_candidates == [{"name": "Delhi", "confidence": 0.9}]
        assert suggestions.scheme_suggestions == ["PM-KISAN"]
        assert suggestions.confidence_score == 0.85
        assert suggestions.reasoning == "High confidence based on context"
        assert suggestions.raw_response == "raw json response"

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        suggestions = PhiSuggestions(
            event_type_suggestions=["rally"],
            confidence_score=0.8,
            reasoning="Test reasoning"
        )

        result = suggestions.to_dict()

        expected = {
            "event_type_suggestions": ["rally"],
            "location_candidates": [],
            "scheme_suggestions": [],
            "confidence_score": 0.8,
            "reasoning": "Test reasoning",
            "raw_response": None
        }
        assert result == expected

    def test_from_dict(self):
        """Should create from dictionary correctly."""
        data = {
            "event_type_suggestions": ["protest"],
            "location_candidates": [{"name": "Mumbai", "confidence": 0.7}],
            "scheme_suggestions": ["Ayushman Bharat"],
            "confidence_score": 0.75,
            "reasoning": "Dictionary reasoning",
            "raw_response": "dict response"
        }

        suggestions = PhiSuggestions.from_dict(data)

        assert suggestions.event_type_suggestions == ["protest"]
        assert suggestions.location_candidates == [{"name": "Mumbai", "confidence": 0.7}]
        assert suggestions.scheme_suggestions == ["Ayushman Bharat"]
        assert suggestions.confidence_score == 0.75
        assert suggestions.reasoning == "Dictionary reasoning"
        assert suggestions.raw_response == "dict response"


class TestPhiAdapter:
    """Unit tests for PhiAdapter."""

    @pytest.fixture
    def mock_ollama_client(self):
        """Mock OllamaClient."""
        return MagicMock()

    @pytest.fixture
    def phi_adapter(self, mock_ollama_client):
        """PhiAdapter with mocked client."""
        adapter = PhiAdapter(enabled=True)
        adapter.client = mock_ollama_client
        return adapter

    @pytest.fixture
    def disabled_phi_adapter(self):
        """Disabled PhiAdapter."""
        return PhiAdapter(enabled=False)

    def test_init_enabled(self):
        """Should initialize enabled adapter."""
        adapter = PhiAdapter(enabled=True, model="phi3.5", base_url="http://test:11434")

        assert adapter.enabled is True
        assert adapter.client is not None
        assert adapter.client.model == "phi3.5"
        assert adapter.client.base_url == "http://test:11434"

    def test_init_disabled(self):
        """Should initialize disabled adapter."""
        adapter = PhiAdapter(enabled=False)

        assert adapter.enabled is False
        assert adapter.client is None

    def test_check_health_enabled_available(self, phi_adapter, mock_ollama_client):
        """Should return True when enabled and client available."""
        mock_ollama_client.check_health.return_value = True

        result = phi_adapter.check_health()

        assert result is True
        mock_ollama_client.check_health.assert_called_once()

    def test_check_health_disabled(self, disabled_phi_adapter):
        """Should return False when disabled."""
        result = disabled_phi_adapter.check_health()

        assert result is False

    def test_suggest_parser_corrections_success(self, phi_adapter, mock_ollama_client):
        """Should successfully get parser correction suggestions."""
        # Mock successful response
        mock_response = {
            "response": '{"event_type_suggestions": ["rally"], "confidence_score": 0.8, "reasoning": "Test reasoning"}',
            "duration_s": 1.5,
            "model": "phi3.5"
        }
        mock_ollama_client.generate.return_value = mock_response

        result = phi_adapter.suggest_parser_corrections(
            tweet_id="tweet-123",
            raw_tweet="Test tweet",
            current_parsed={"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == ["rally"]
        assert result.confidence_score == 0.8
        assert result.reasoning == "Test reasoning"
        assert result.raw_response == mock_response["response"]

    def test_suggest_parser_corrections_disabled(self, disabled_phi_adapter):
        """Should return empty suggestions when disabled."""
        result = disabled_phi_adapter.suggest_parser_corrections(
            tweet_id="tweet-123",
            raw_tweet="Test tweet",
            current_parsed={"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []
        assert result.confidence_score == 0.0

    def test_suggest_parser_corrections_client_error(self, phi_adapter, mock_ollama_client):
        """Should handle client errors gracefully."""
        mock_ollama_client.generate.return_value = {"error": "Model unavailable"}

        result = phi_adapter.suggest_parser_corrections(
            tweet_id="tweet-123",
            raw_tweet="Test tweet",
            current_parsed={"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []

    def test_suggest_geo_disambiguation_success(self, phi_adapter, mock_ollama_client):
        """Should successfully get geo disambiguation suggestions."""
        mock_response = {
            "response": '{"location_candidates": [{"name": "Delhi", "confidence": 0.9}], "confidence_score": 0.85}',
            "duration_s": 1.2,
            "model": "phi3.5"
        }
        mock_ollama_client.generate.return_value = mock_response

        result = phi_adapter.suggest_geo_disambiguation(
            tweet_id="tweet-456",
            raw_tweet="Delhi rally",
            location_candidates=["Delhi", "Mumbai"]
        )

        assert isinstance(result, PhiSuggestions)
        assert result.location_candidates == [{"name": "Delhi", "confidence": 0.9}]
        assert result.confidence_score == 0.85

    def test_rank_event_type_candidates_success(self, phi_adapter, mock_ollama_client):
        """Should successfully rank event type candidates."""
        mock_response = {
            "response": '{"event_type_suggestions": ["rally", "protest"], "confidence_score": 0.75}',
            "duration_s": 1.0,
            "model": "phi3.5"
        }
        mock_ollama_client.generate.return_value = mock_response

        result = phi_adapter.rank_event_type_candidates(
            tweet_id="tweet-789",
            raw_tweet="Big protest in city",
            candidates=["rally", "meeting", "protest"]
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == ["rally", "protest"]
        assert result.confidence_score == 0.75

    def test_parse_correction_response_invalid_json(self, phi_adapter, mock_ollama_client):
        """Should handle invalid JSON responses gracefully."""
        mock_ollama_client.generate.return_value = {
            "response": "invalid json {",
            "duration_s": 1.0,
            "model": "phi3.5"
        }

        result = phi_adapter.suggest_parser_corrections(
            tweet_id="tweet-123",
            raw_tweet="Test tweet",
            current_parsed={"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []

    @pytest.mark.asyncio
    async def test_cognitive_interface_suggestions(self):
        """Should integrate Phi adapter through cognitive interface."""
        # Mock Phi adapter
        mock_adapter = MagicMock()
        mock_adapter.enabled = True
        mock_adapter.suggest_parser_corrections.return_value = PhiSuggestions(
            event_type_suggestions=["rally"],
            confidence_score=0.8
        )

        interface = CognitiveInterface(phi_adapter=mock_adapter)

        result = await interface.suggest_parser_enhancements(
            tweet_id="tweet-123",
            raw_tweet="Test tweet",
            current_parsed={"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == ["rally"]
        mock_adapter.suggest_parser_corrections.assert_called_once()

    @pytest.mark.asyncio
    async def test_cognitive_interface_disabled_phi(self):
        """Should handle disabled Phi adapter gracefully."""
        mock_adapter = MagicMock()
        mock_adapter.enabled = False
        mock_adapter.suggest_parser_corrections.return_value = PhiSuggestions()

        interface = CognitiveInterface(phi_adapter=mock_adapter)

        result = await interface.suggest_parser_enhancements(
            tweet_id="tweet-123",
            raw_tweet="Test tweet",
            current_parsed={"event_type": "meeting"}
        )

        assert isinstance(result, PhiSuggestions)
        assert result.event_type_suggestions == []

    def test_cognitive_readiness_check(self):
        """Should check cognitive component readiness."""
        # Test with enabled adapter
        mock_adapter = MagicMock()
        mock_adapter.enabled = True
        mock_adapter.check_health.return_value = True

        interface = CognitiveInterface(phi_adapter=mock_adapter)
        status = interface.check_cognitive_readiness()

        assert status["cognitive_services_ready"] is True
        assert status["phi_3_5_enabled"] is True
        assert status["phi_3_5_available"] is True
        assert len(status["cognitive_capabilities"]) > 0

        # Test with disabled adapter
        mock_adapter.enabled = False
        status = interface.check_cognitive_readiness()

        assert status["cognitive_services_ready"] is False
        assert status["phi_3_5_enabled"] is False
        assert status["cognitive_capabilities"] == []

    def test_cognitive_status_detail(self):
        """Should provide detailed cognitive status."""
        mock_adapter = MagicMock()
        mock_adapter.enabled = True
        mock_adapter.check_health.return_value = False
        mock_adapter.client = MagicMock()
        mock_adapter.client.model = "phi3.5"

        interface = CognitiveInterface(phi_adapter=mock_adapter)
        status = interface.get_cognitive_status()

        assert status["phi_3_5"]["enabled"] is True
        assert status["phi_3_5"]["available"] is False
        assert status["phi_3_5"]["model"] == "phi3.5"
        assert isinstance(status["capabilities"], list)

    def test_prompt_building(self, phi_adapter):
        """Should build prompts correctly."""
        # Test correction prompt
        prompt = phi_adapter._build_correction_prompt(
            "Test tweet text",
            {"event_type": "meeting"}
        )

        assert "Test tweet text" in prompt
        assert "meeting" in prompt
        assert "event_type_suggestions" in prompt

        # Test geo prompt
        geo_prompt = phi_adapter._build_geo_prompt(
            "Location tweet",
            ["Delhi", "Mumbai"]
        )

        assert "Location tweet" in geo_prompt
        assert "Delhi" in geo_prompt
        assert "Mumbai" in geo_prompt

        # Test event ranking prompt
        event_prompt = phi_adapter._build_event_ranking_prompt(
            "Event tweet",
            ["rally", "meeting"]
        )

        assert "Event tweet" in event_prompt
        assert "rally" in event_prompt
        assert "meeting" in event_prompt

    def test_system_prompts(self, phi_adapter):
        """Should provide appropriate system prompts."""
        correction_prompt = phi_adapter._get_correction_system_prompt()
        assert "Indian government communications" in correction_prompt

        geo_prompt = phi_adapter._get_geo_system_prompt()
        assert "geographic expert" in geo_prompt

        event_prompt = phi_adapter._get_event_ranking_system_prompt()
        assert "social and government events" in event_prompt