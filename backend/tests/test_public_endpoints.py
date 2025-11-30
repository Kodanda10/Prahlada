"""
Integration tests for public (unauthenticated) API endpoints.

Tests cover:
- Root endpoint (/)
- Configuration endpoint (/config)
- Health check endpoints (/health/*)
"""

import os
import pytest

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from httpx import AsyncClient


class TestRootEndpoint:
    """Tests for the root endpoint."""

    @pytest.mark.asyncio
    async def test_root_returns_status(self, async_client: AsyncClient):
        """Root endpoint should return running status."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "Project Dhruv API is running" in data["status"]

    @pytest.mark.asyncio
    async def test_root_response_is_json(self, async_client: AsyncClient):
        """Root endpoint should return JSON content type."""
        response = await async_client.get("/")
        
        assert response.headers["content-type"] == "application/json"


class TestConfigEndpoint:
    """Tests for the configuration endpoint."""

    @pytest.mark.asyncio
    async def test_config_returns_titles(self, async_client: AsyncClient):
        """Config endpoint should return UI titles."""
        response = await async_client.get("/config")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "titles" in data
        assert "app_title" in data["titles"]
        assert "app_subtitle" in data["titles"]

    @pytest.mark.asyncio
    async def test_config_returns_modules(self, async_client: AsyncClient):
        """Config endpoint should return module flags."""
        response = await async_client.get("/config")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "modules" in data
        assert "analytics" in data["modules"]
        assert "review" in data["modules"]
        assert "control_hub" in data["modules"]

    @pytest.mark.asyncio
    async def test_config_module_flags_are_boolean(self, async_client: AsyncClient):
        """Module flags should be boolean values."""
        response = await async_client.get("/config")
        data = response.json()
        
        for module, enabled in data["modules"].items():
            assert isinstance(enabled, bool), f"Module {module} should be boolean"

    @pytest.mark.asyncio
    async def test_config_titles_are_strings(self, async_client: AsyncClient):
        """Title values should be strings."""
        response = await async_client.get("/config")
        data = response.json()
        
        for key, value in data["titles"].items():
            assert isinstance(value, str), f"Title {key} should be string"

    @pytest.mark.asyncio
    async def test_config_contains_hindi_titles(self, async_client: AsyncClient):
        """Config should contain Hindi titles for localization."""
        response = await async_client.get("/config")
        data = response.json()
        
        # Check for Hindi characters in titles (Devanagari script)
        app_title = data["titles"]["app_title"]
        # Simple check for Hindi Unicode range
        has_hindi = any('\u0900' <= char <= '\u097F' for char in app_title)
        assert has_hindi, "App title should contain Hindi characters"


class TestSystemHealthEndpoint:
    """Tests for the system health endpoint."""

    @pytest.mark.asyncio
    async def test_health_system_returns_status(self, async_client: AsyncClient):
        """System health should return overall status."""
        response = await async_client.get("/health/system")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_health_system_returns_cpu_usage(self, async_client: AsyncClient):
        """System health should include CPU usage."""
        response = await async_client.get("/health/system")
        data = response.json()
        
        assert "cpu_usage" in data
        assert isinstance(data["cpu_usage"], (int, float))
        assert 0 <= data["cpu_usage"] <= 100

    @pytest.mark.asyncio
    async def test_health_system_returns_memory_usage(self, async_client: AsyncClient):
        """System health should include memory usage."""
        response = await async_client.get("/health/system")
        data = response.json()
        
        assert "memory_usage" in data
        assert isinstance(data["memory_usage"], (int, float))
        assert 0 <= data["memory_usage"] <= 100

    @pytest.mark.asyncio
    async def test_health_system_returns_services(self, async_client: AsyncClient):
        """System health should return service statuses."""
        response = await async_client.get("/health/system")
        data = response.json()
        
        assert "services" in data
        services = data["services"]
        
        # Check expected services
        expected_services = ["ollama", "cognitive_engine", "database_file", "mapbox_integration"]
        for service in expected_services:
            assert service in services, f"Missing service: {service}"
            assert "status" in services[service]

    @pytest.mark.asyncio
    async def test_health_system_service_status_values(self, async_client: AsyncClient):
        """Service status should be valid values."""
        response = await async_client.get("/health/system")
        data = response.json()
        
        valid_statuses = ["up", "down", "degraded", "unknown"]
        for service_name, service_data in data["services"].items():
            assert service_data["status"] in valid_statuses, \
                f"Invalid status for {service_name}"

    @pytest.mark.asyncio
    async def test_health_system_returns_performance_metrics(self, async_client: AsyncClient):
        """System health should include performance metrics."""
        response = await async_client.get("/health/system")
        data = response.json()
        
        # Check for latency metrics
        assert "p95_latency_ms" in data
        assert isinstance(data["p95_latency_ms"], (int, float))
        
        # Check for error rate
        assert "api_error_rate" in data
        assert isinstance(data["api_error_rate"], (int, float))


class TestAnalyticsHealthEndpoint:
    """Tests for the analytics health endpoint."""

    @pytest.mark.asyncio
    async def test_health_analytics_returns_freshness(self, async_client: AsyncClient):
        """Analytics health should return data freshness info."""
        response = await async_client.get("/health/analytics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "data_freshness" in data
        freshness = data["data_freshness"]
        
        assert "status" in freshness
        assert freshness["status"] in ["fresh", "stale", "unknown"]

    @pytest.mark.asyncio
    async def test_health_analytics_returns_timestamp(self, async_client: AsyncClient):
        """Analytics health should include last update timestamp."""
        response = await async_client.get("/health/analytics")
        data = response.json()
        
        freshness = data["data_freshness"]
        assert "last_updated" in freshness
        assert isinstance(freshness["last_updated"], int)

    @pytest.mark.asyncio
    async def test_health_analytics_returns_modules(self, async_client: AsyncClient):
        """Analytics health should return module status."""
        response = await async_client.get("/health/analytics")
        data = response.json()
        
        assert "modules" in data
        modules = data["modules"]
        
        # Check module structure
        for module_name, module_data in modules.items():
            assert "status" in module_data
            assert "cache_hit" in module_data

    @pytest.mark.asyncio
    async def test_health_analytics_returns_data_source(self, async_client: AsyncClient):
        """Analytics health should indicate data source."""
        response = await async_client.get("/health/analytics")
        data = response.json()
        
        assert "source" in data["data_freshness"]


class TestEndpointMethods:
    """Tests for HTTP method handling on public endpoints."""

    @pytest.mark.asyncio
    async def test_root_rejects_post(self, async_client: AsyncClient):
        """Root endpoint should reject POST requests."""
        response = await async_client.post("/")
        
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_config_rejects_put(self, async_client: AsyncClient):
        """Config endpoint should reject PUT requests."""
        response = await async_client.put("/config", json={})
        
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_health_rejects_delete(self, async_client: AsyncClient):
        """Health endpoints should reject DELETE requests."""
        response = await async_client.delete("/health/system")
        
        assert response.status_code == 405
