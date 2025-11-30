"""
Centralized configuration management for the backend.

Uses environment variables with sensible defaults.
"""

import os
from typing import List, Optional, Dict, Any
from functools import lru_cache
from enum import Enum


class Environment(str, Enum):
    """Environment profiles for the application."""
    LOCAL = "local"
    TEST = "test"
    PRODUCTION = "prod"


class Settings:
    """
    Application settings loaded from environment variables with profile support.

    Supports different configurations for local development, testing, and production.
    """

    # --- Environment Profile ---
    ENV: Environment = Environment(os.getenv("ENV", "local").lower())

    # --- Application ---
    APP_NAME: str = "Project Prahlada API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # --- Authentication ---
    AUTH_SECRET_KEY: str = os.getenv("AUTH_SECRET_KEY", "")
    AUTH_ALGORITHM: str = os.getenv("AUTH_ALGORITHM", "HS256")
    AUTH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("AUTH_TOKEN_EXPIRE_MINUTES", "60"))

    # --- CORS ---
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # --- Vector Store ---
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "data/faiss_index.bin")
    FAISS_EMBEDDING_MODEL: str = os.getenv("FAISS_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # --- Cognitive / Phi 3.5 ---
    USE_PHI_LOCAL: bool = os.getenv("USE_PHI_LOCAL", "false").lower() == "true"
    PHI_BASE_URL: str = os.getenv("PHI_BASE_URL", "http://localhost:11434")
    PHI_MODEL: str = os.getenv("PHI_MODEL", "phi3.5")
    PHI_BACKUP_MODEL: str = os.getenv("PHI_BACKUP_MODEL", "gemma2:2b")
    PHI_REQUEST_TIMEOUT: int = int(os.getenv("PHI_REQUEST_TIMEOUT", "30"))

    # --- Admin ---
    ADMIN_USERNAME: Optional[str] = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD: Optional[str] = os.getenv("ADMIN_PASSWORD")

    # --- Logging ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # --- Paths ---
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    LEARNED_RULES_DIR: str = os.getenv("LEARNED_RULES_DIR", "backend/learned_rules")

    def __init__(self):
        """Validate required settings on initialization."""
        self._validate()
        self._apply_environment_overrides()

    def _validate(self):
        """Validate that required settings are present."""
        required_in_production = []

        if self.ENV == Environment.PRODUCTION:
            required_in_production = ["AUTH_SECRET_KEY", "DATABASE_URL"]

        for setting in required_in_production:
            value = getattr(self, setting, "")
            if not value:
                raise ValueError(f"Required setting '{setting}' is not configured for {self.ENV.value} environment")

    def _apply_environment_overrides(self):
        """Apply environment-specific overrides."""
        if self.ENV == Environment.TEST:
            # Test-specific overrides
            self.DEBUG = True
            self.LOG_LEVEL = "WARNING"
            self.USE_PHI_LOCAL = False  # Disable Phi in tests by default
            if not self.DATABASE_URL:
                self.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
            if not self.AUTH_SECRET_KEY:
                self.AUTH_SECRET_KEY = "test-secret-key-for-testing-only"

        elif self.ENV == Environment.LOCAL:
            # Local development overrides
            self.DEBUG = True
            self.USE_PHI_LOCAL = False  # Conservative default for local dev
            if not self.DATABASE_URL:
                self.DATABASE_URL = "sqlite+aiosqlite:///./data/local.db"

        elif self.ENV == Environment.PRODUCTION:
            # Production overrides
            self.DEBUG = False
            self.LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENV == Environment.PRODUCTION

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.ENV == Environment.TEST

    @property
    def is_local(self) -> bool:
        """Check if running in local development mode."""
        return self.ENV == Environment.LOCAL

    @property
    def has_admin_credentials(self) -> bool:
        """Check if admin credentials are configured."""
        return bool(self.ADMIN_USERNAME and self.ADMIN_PASSWORD)

    @property
    def phi_config(self) -> Dict[str, Any]:
        """Get Phi 3.5 configuration as a dictionary."""
        return {
            "enabled": self.USE_PHI_LOCAL,
            "base_url": self.PHI_BASE_URL,
            "model": self.PHI_MODEL,
            "backup_model": self.PHI_BACKUP_MODEL,
            "timeout": self.PHI_REQUEST_TIMEOUT
        }

    def get_environment_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current environment configuration.

        Useful for health checks and debugging.
        """
        return {
            "environment": self.ENV.value,
            "debug": self.DEBUG,
            "database_configured": bool(self.DATABASE_URL),
            "auth_configured": bool(self.AUTH_SECRET_KEY),
            "phi_enabled": self.USE_PHI_LOCAL,
            "vector_store_model": self.FAISS_EMBEDDING_MODEL,
            "log_level": self.LOG_LEVEL,
            "admin_configured": self.has_admin_credentials
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()


# Global settings instance for convenience
settings = get_settings()
