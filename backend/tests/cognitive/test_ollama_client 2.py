"""
Tests for cognitive service: Ollama LLM client.
Mocks HTTP requests to test client logic without needing actual Ollama service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from backend.cognitive.ollama_client import OllamaClient


class TestOllamaClient:
    """Test Ollama LLM client."""
    
    def test_client_initialization(self):
        """Client should initialize with correct defaults."""
        client = OllamaClient()
        
        assert client.base_url == "http://localhost:11434"
        assert client.model == "gemma2:9b"
        assert client.backup_model == "phi3.5"
    
    def test_custom_initialization(self):
        """Client should accept custom parameters."""
        client = OllamaClient(
            base_url="http://custom:8080",
            model="llama2",
            backup_model="mistral"
        )
        
        assert client.base_url == "http://custom:8080"
        assert client.model == "llama2"
        assert client.backup_model == "mistral"
    
    @patch('urllib.request.urlopen')
    def test_generate_success(self, mock_urlopen):
        """Generate should return response on success."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "response": "The sky is blue because of Rayleigh scattering."
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("Why is the sky blue?")
        
        assert "response" in result
        assert "The sky is blue" in result["response"]
        assert "duration_s" in result
        assert "model" in result
        assert result["model"] == "gemma2:9b"
    
    @patch('urllib.request.urlopen')
    def test_generate_with_system_prompt(self, mock_urlopen):
        """Generate should include system prompt when provided."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "response": "Test response"
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate(
            "Test question",
            system_prompt="Answer briefly."
        )
        
        assert "response" in result
        assert result["response"] == "Test response"
    
    @patch('urllib.request.urlopen')
    def test_generate_json_mode(self, mock_urlopen):
        """Generate should request JSON format when json_mode=True."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "response": '{"key": "value"}'
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("Extract data", json_mode=True)
        
        assert "response" in result
    
    @patch('urllib.request.urlopen')
    def test_generate_primary_failure_uses_backup(self, mock_urlopen):
        """Should use backup model when primary fails."""
        # First call fails, second succeeds
        mock_urlopen.side_effect = [
            Exception("Model not found"),
            MagicMock(
                __enter__=lambda self: self,
                __exit__=lambda *args: None,
                read=lambda: json.dumps({"response": "Backup response"}).encode('utf-8')
            )
        ]
        
        client = OllamaClient()
        result = client.generate("Test")
        
        assert "response" in result
        assert result["response"] == "Backup response"
        assert result["model"] == "phi3.5"
    
    @patch('urllib.request.urlopen')
    def test_generate_both_models_fail(self, mock_urlopen):
        """Should return error when both models fail."""
        mock_urlopen.side_effect = Exception("Connection refused")
        
        client = OllamaClient()
        result = client.generate("Test")
        
        assert "error" in result
        assert "Connection refused" in result["error"]
    
    @patch('urllib.request.urlopen')
    def test_check_health_success(self, mock_urlopen):
        """Health check should return True when service is available."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        client = OllamaClient()
        assert client.check_health() is True
    
    @patch('urllib.request.urlopen')
    def test_check_health_failure(self, mock_urlopen):
        """Health check should return False when service is unavailable."""
        mock_urlopen.side_effect = Exception("Connection refused")
        
        client = OllamaClient()
        assert client.check_health() is False
    
    @patch('urllib.request.urlopen')
    def test_generate_handles_network_error(self, mock_urlopen):
        """Generate should handle network errors gracefully."""
        mock_urlopen.side_effect = Exception("Network timeout")
        
        client = OllamaClient(backup_model=None)  # No backup
        result = client.generate("Test")
        
        assert "error" in result
        assert "Network timeout" in result["error"]
    
    @patch('urllib.request.urlopen')
    def test_generate_measures_duration(self, mock_urlopen):
        """Generate should measure request duration."""
        import time
        
        def slow_response(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow response
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps({"response": "Slow response"}).encode('utf-8')
            mock_resp.__enter__.return_value = mock_resp
            return mock_resp
        
        mock_urlopen.side_effect = slow_response
        
        client = OllamaClient()
        result = client.generate("Test")
        
        assert "duration_s" in result
        assert result["duration_s"] > 0.1
