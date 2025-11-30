"""
Unit tests for the authentication module.

Tests cover:
- Password hashing and verification
- JWT token creation and validation
- User authentication logic
"""

import os
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from jose import jwt, JWTError

from backend.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_user_by_username,
    authenticate_user,
    get_current_user,
    ensure_default_admin,
    SECRET_KEY,
    ALGORITHM,
)
from backend.models import AdminUser


class TestPasswordHashing:
    """Tests for password hashing utilities."""

    def test_hash_password_returns_different_value(self):
        """Password hash should differ from plaintext."""
        password = "securepassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_produces_unique_hashes(self):
        """Same password should produce different hashes (due to salt)."""
        password = "securepassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Bcrypt includes random salt, so hashes should differ
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Correct password should verify successfully."""
        password = "correctpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Incorrect password should fail verification."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_string(self):
        """Empty password should fail verification against real hash."""
        password = "realpassword"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False

    def test_hash_special_characters(self):
        """Password with special characters should hash correctly."""
        password = "P@$$w0rd!#$%^&*()"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_hash_unicode_password(self):
        """Unicode passwords should hash correctly."""
        password = "पासवर्ड123"  # Hindi characters
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Tests for JWT token creation and validation."""

    def test_create_access_token_basic(self):
        """Token creation should return a valid JWT string."""
        data = {"sub": "testuser", "uid": "user-123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_payload(self):
        """Token should contain the original payload data."""
        data = {"sub": "testuser", "uid": "user-123", "roles": ["admin"]}
        token = create_access_token(data)
        
        # Decode and verify
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == "testuser"
        assert decoded["uid"] == "user-123"
        assert decoded["roles"] == ["admin"]

    def test_create_access_token_has_expiration(self):
        """Token should include expiration claim."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert "exp" in decoded
        assert decoded["exp"] > datetime.utcnow().timestamp()

    def test_create_access_token_custom_expiration(self):
        """Token expiration should respect custom delta."""
        data = {"sub": "testuser"}
        
        # Create two tokens with different expiration times
        short_expires = timedelta(minutes=1)
        long_expires = timedelta(minutes=10)
        
        token_short = create_access_token(data, expires_delta=short_expires)
        token_long = create_access_token(data, expires_delta=long_expires)
        
        decoded_short = jwt.decode(token_short, SECRET_KEY, algorithms=[ALGORITHM])
        decoded_long = jwt.decode(token_long, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify both have expiration
        assert "exp" in decoded_short
        assert "exp" in decoded_long
        
        # The longer expiration token should have a later exp timestamp
        assert decoded_long["exp"] > decoded_short["exp"], \
            "Longer expiration should result in later timestamp"
        
        # Difference should be approximately 9 minutes (540 seconds)
        time_diff = decoded_long["exp"] - decoded_short["exp"]
        assert 500 < time_diff < 600, f"Expected ~540s difference, got {time_diff}s"

    def test_expired_token_raises_error(self):
        """Decoding an expired token should raise JWTError."""
        data = {"sub": "testuser"}
        # Create token that expired 1 second ago
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(JWTError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_invalid_token_signature(self):
        """Token with wrong secret should fail validation."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong-secret-key", algorithms=[ALGORITHM])

    def test_token_with_empty_payload(self):
        """Empty payload should still create valid token."""
        token = create_access_token({})
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert "exp" in decoded


class TestGetUserByUsername:
    """Tests for user lookup by username."""

    @pytest_asyncio.fixture
    async def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_get_user_found(self, mock_db_session):
        """Should return user when found in database."""
        mock_user = AdminUser(
            id="user-123",
            username="existinguser",
            password_hash="hashed",
            roles=["admin"],
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result
        
        result = await get_user_by_username(mock_db_session, "existinguser")
        
        assert result is not None
        assert result.username == "existinguser"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, mock_db_session):
        """Should return None when user not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await get_user_by_username(mock_db_session, "nonexistent")
        
        assert result is None


class TestAuthenticateUser:
    """Tests for user authentication logic."""

    @pytest.mark.asyncio
    async def test_authenticate_valid_credentials(self):
        """Valid credentials should return user object."""
        mock_user = AdminUser(
            id="user-123",
            username="validuser",
            password_hash=get_password_hash("correctpassword"),
            is_active=True,
        )
        
        with patch("backend.auth.get_user_by_username", return_value=mock_user):
            mock_db = AsyncMock()
            result = await authenticate_user(mock_db, "validuser", "correctpassword")
            
            assert result is not None
            assert result.username == "validuser"

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self):
        """Wrong password should return None."""
        mock_user = AdminUser(
            id="user-123",
            username="validuser",
            password_hash=get_password_hash("correctpassword"),
            is_active=True,
        )
        
        with patch("backend.auth.get_user_by_username", return_value=mock_user):
            mock_db = AsyncMock()
            result = await authenticate_user(mock_db, "validuser", "wrongpassword")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_user(self):
        """Nonexistent user should return None."""
        with patch("backend.auth.get_user_by_username", return_value=None):
            mock_db = AsyncMock()
            result = await authenticate_user(mock_db, "nonexistent", "anypassword")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self):
        """Inactive user should return None."""
        mock_user = AdminUser(
            id="user-123",
            username="inactiveuser",
            password_hash=get_password_hash("correctpassword"),
            is_active=False,
        )
        
        with patch("backend.auth.get_user_by_username", return_value=mock_user):
            mock_db = AsyncMock()
            result = await authenticate_user(mock_db, "inactiveuser", "correctpassword")
            
            assert result is None


class TestEnsureDefaultAdmin:
    """Tests for default admin user provisioning."""

    @pytest.mark.asyncio
    async def test_creates_admin_when_not_exists(self):
        """Should create admin user when not found."""
        mock_db = AsyncMock()
        
        with patch("backend.auth.get_user_by_username", return_value=None):
            await ensure_default_admin(mock_db, "newadmin", "adminpassword")
            
            # Verify user was added and committed
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            
            # Verify the added user has correct attributes
            added_user = mock_db.add.call_args[0][0]
            assert added_user.username == "newadmin"
            assert added_user.roles == ["admin"]

    @pytest.mark.asyncio
    async def test_skips_when_admin_exists(self):
        """Should not create user if already exists."""
        existing_user = AdminUser(
            id="existing-id",
            username="existingadmin",
            password_hash="existing_hash",
        )
        
        mock_db = AsyncMock()
        
        with patch("backend.auth.get_user_by_username", return_value=existing_user):
            await ensure_default_admin(mock_db, "existingadmin", "password")
            
            # Verify no user was added
            mock_db.add.assert_not_called()
            mock_db.commit.assert_not_called()


    def test_verify_password_additional_edge_cases(self):
        """Additional edge cases for password verification."""
        # Test with very long password
        long_password = "a" * 1000
        hashed = get_password_hash(long_password)
        assert verify_password(long_password, hashed)

        # Test with password containing special characters
        special_password = "!@#$%^&*()_+-=[]{}|;:,.<>?`~"
        hashed = get_password_hash(special_password)
        assert verify_password(special_password, hashed)

    def test_create_access_token_edge_cases(self):
        """Test token creation with edge cases."""
        # Empty payload
        token = create_access_token({})
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded

        # Very long username
        long_username = "user" * 100
        token = create_access_token({"sub": long_username})
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == long_username

    def test_jwt_decode_edge_cases(self):
        """Test JWT decoding edge cases."""
        # Valid token
        data = {"sub": "test", "custom": "data"}
        token = create_access_token(data)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test"
        assert decoded["custom"] == "data"
        assert "exp" in decoded

        # Token with future expiration
        future_token = create_access_token(data, timedelta(hours=24))
        decoded = jwt.decode(future_token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["exp"] > datetime.utcnow().timestamp()
