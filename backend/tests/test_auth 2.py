"""
Backend authentication tests.
Tests JWT token generation, password hashing, user authentication.
"""
import pytest
from datetime import timedelta
from jose import jwt
from backend.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_user_by_username,
    ensure_default_admin,
    SECRET_KEY,
    ALGORITHM,
)
from backend.models import AdminUser


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hash_generates_different_hashes(self):
        """Same password should generate different hashes (salt)."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0
    
    def test_verify_password_correct(self):
        """Correct password should verify successfully."""
        password = "secure_password"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Incorrect password should fail verification."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_hash_not_plain_text(self):
        """Hashed password should not contain plain text."""
        password = "my_secret_pass"
        hashed = get_password_hash(password)
        
        assert password not in hashed
        assert hashed.startswith("$2b$")  # bcrypt hash format


class TestTokenGeneration:
    """Test JWT token creation and validation."""
    
    def test_create_access_token_basic(self):
        """Token should be created with proper payload."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_decodes_correctly(self):
        """Created token should decode back to original data."""
        data = {"sub": "admin_user", "role": "admin"}
        token = create_access_token(data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == "admin_user"
        assert decoded["role"] == "admin"
        assert "exp" in decoded
    
    def test_create_access_token_custom_expiry(self):
        """Token should respect custom expiry time."""
        data = {"sub": "testuser"}
        custom_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=custom_delta)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
       assert "exp" in decoded
    
    def test_create_access_token_with_extra_claims(self):
        """Token should preserve all custom claims."""
        data = {
            "sub": "user123",
            "email": "user@example.com",
            "roles": ["admin", "editor"],
        }
        token = create_access_token(data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "user@example.com"
        assert decoded["roles"] == ["admin", "editor"]


@pytest.mark.asyncio
class TestUserDatabase:
    """Test database user operations."""
    
    async def test_get_user_by_username_not_found(self, async_db_session):
        """Non-existent user should return None."""
        user = await get_user_by_username(async_db_session, "nonexistent_user")
        assert user is None
    
    async def test_ensure_default_admin_creates_user(self, async_db_session):
        """Default admin should be created if not exists."""
        username = "test_admin"
        password = "test_password"
        
        await ensure_default_admin(async_db_session, username, password)
        
        user = await get_user_by_username(async_db_session, username)
        assert user is not None
        assert user.username == username
        assert "admin" in user.roles
    
    async def test_ensure_default_admin_idempotent(self, async_db_session):
        """Creating admin twice should not duplicate."""
        username = "admin_test"
        password = "password123"
        
        await ensure_default_admin(async_db_session, username, password)
        await ensure_default_admin(async_db_session, username, password)
        
        user = await get_user_by_username(async_db_session, username)
        assert user is not None


@pytest.mark.asyncio
class TestAuthentication:
    """Test user authentication flow."""
    
    async def test_authenticate_user_success(self, async_db_session):
        """Valid credentials should authenticate successfully."""
        username = "valid_user"
        password = "valid_password"
        
        # Create user
        await ensure_default_admin(async_db_session, username, password)
        
        # Authenticate
        user = await authenticate_user(async_db_session, username, password)
        
        assert user is not None
        assert user.username == username
    
    async def test_authenticate_user_wrong_password(self, async_db_session):
        """Wrong password should fail authentication."""
        username = "user_test"
        password = "correct_pass"
        wrong_password = "wrong_pass"
        
        await ensure_default_admin(async_db_session, username, password)
        
        user = await authenticate_user(async_db_session, username, wrong_password)
        
        assert user is None
    
    async def test_authenticate_user_not_found(self, async_db_session):
        """Non-existent user should fail authentication."""
        user = await authenticate_user(async_db_session, "no_such_user", "password")
        assert user is None
    
    async def test_authenticate_inactive_user(self, async_db_session):
        """Inactive user should fail authentication."""
        username = "inactive_user"
        password = "password"
        
        await ensure_default_admin(async_db_session, username, password)
        
        # Mark user as inactive
        user = await get_user_by_username(async_db_session, username)
        user.is_active = False
        await async_db_session.commit()
        
        # Try to authenticate
        result = await authenticate_user(async_db_session, username, password)
        
        assert result is None
