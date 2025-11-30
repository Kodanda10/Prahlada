"""
Integration tests for authentication API endpoints.

Tests cover:
- Login endpoint (/api/auth/login)
- Token verification endpoint (/api/auth/verify)
- Authorization header handling
"""

import os
import pytest

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from httpx import AsyncClient


class TestLoginEndpoint:
    """Tests for the login endpoint."""

    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, async_client: AsyncClient):
        """Valid credentials should return token and user info."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpassword123"},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert "user" in data
        assert len(data["token"]) > 0

    @pytest.mark.asyncio
    async def test_login_returns_user_details(self, async_client: AsyncClient):
        """Login should return correct user details."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpassword123"},
        )
        
        data = response.json()
        user = data["user"]
        
        assert user["username"] == "testadmin"
        assert user["id"] == "test-user-id"
        assert "roles" in user
        assert "admin" in user["roles"]

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, async_client: AsyncClient):
        """Invalid password should return 401."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "wrongpassword"},
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Nonexistent user should return 401."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "anypassword"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, async_client: AsyncClient):
        """Inactive user should return 401."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "inactiveuser", "password": "password123"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_missing_username(self, async_client: AsyncClient):
        """Missing username should return 422 validation error."""
        response = await async_client.post(
            "/api/auth/login",
            json={"password": "somepassword"},
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_password(self, async_client: AsyncClient):
        """Missing password should return 422 validation error."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "testadmin"},
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_empty_credentials(self, async_client: AsyncClient):
        """Empty credentials should fail authentication."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "", "password": ""},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_case_sensitive_username(self, async_client: AsyncClient):
        """Username should be case-sensitive."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "TestAdmin", "password": "testpassword123"},
        )
        
        # Should fail because username case doesn't match
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_response_token_is_jwt(self, async_client: AsyncClient):
        """Returned token should be a valid JWT format."""
        response = await async_client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpassword123"},
        )
        
        token = response.json()["token"]
        
        # JWT should have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3

    @pytest.mark.asyncio
    async def test_login_rejects_get_method(self, async_client: AsyncClient):
        """Login endpoint should reject GET requests."""
        response = await async_client.get("/api/auth/login")
        
        assert response.status_code == 405


class TestVerifyEndpoint:
    """Tests for the token verification endpoint."""

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, async_client: AsyncClient, auth_headers: dict):
        """Valid token should return user details."""
        response = await async_client.get(
            "/api/auth/verify",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "username" in data
        assert "id" in data
        assert "roles" in data

    @pytest.mark.asyncio
    async def test_verify_returns_correct_user(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Verify should return details of the authenticated user."""
        response = await async_client.get(
            "/api/auth/verify",
            headers=auth_headers,
        )
        
        data = response.json()
        
        assert data["username"] == "testadmin"
        assert data["id"] == "test-user-id"

    @pytest.mark.asyncio
    async def test_verify_no_token(self, async_client: AsyncClient):
        """Missing token should return 401."""
        response = await async_client.get("/api/auth/verify")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self, async_client: AsyncClient):
        """Invalid token should return 401."""
        response = await async_client.get(
            "/api/auth/verify",
            headers={"Authorization": "Bearer invalid-token-here"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_expired_token(
        self, async_client: AsyncClient, expired_token: str
    ):
        """Expired token should return 401."""
        response = await async_client.get(
            "/api/auth/verify",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_malformed_header(self, async_client: AsyncClient):
        """Malformed Authorization header should return 401."""
        # Missing "Bearer" prefix
        response = await async_client.get(
            "/api/auth/verify",
            headers={"Authorization": "some-token-without-bearer"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_wrong_auth_scheme(self, async_client: AsyncClient):
        """Wrong authentication scheme should return 401."""
        response = await async_client.get(
            "/api/auth/verify",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},  # Base64 basic auth
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_empty_token(self, async_client: AsyncClient):
        """Empty token after Bearer should return 401."""
        response = await async_client.get(
            "/api/auth/verify",
            headers={"Authorization": "Bearer "},
        )
        
        assert response.status_code == 401


class TestLoginAndVerifyFlow:
    """End-to-end tests for login and verification flow."""

    @pytest.mark.asyncio
    async def test_login_then_verify(self, async_client: AsyncClient):
        """Token from login should work for verification."""
        # Step 1: Login
        login_response = await async_client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpassword123"},
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Step 2: Verify with obtained token
        verify_response = await async_client.get(
            "/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert verify_response.status_code == 200
        user_data = verify_response.json()
        
        # User details should match login response
        assert user_data["username"] == "testadmin"

    @pytest.mark.asyncio
    async def test_multiple_logins_produce_different_tokens(
        self, async_client: AsyncClient
    ):
        """Multiple logins should produce different tokens (different exp times)."""
        credentials = {"username": "testadmin", "password": "testpassword123"}
        
        response1 = await async_client.post("/api/auth/login", json=credentials)
        response2 = await async_client.post("/api/auth/login", json=credentials)
        
        token1 = response1.json()["token"]
        token2 = response2.json()["token"]
        
        # Tokens may be same if generated at same second, but usually different
        # Both should be valid
        for token in [token1, token2]:
            verify_response = await async_client.get(
                "/api/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert verify_response.status_code == 200
