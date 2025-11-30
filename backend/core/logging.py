"""
Structured logging configuration for the backend.

Provides consistent logging across all modules with:
- Structured log format
- Request correlation IDs
- Appropriate log levels
"""

import logging
import sys
from typing import Optional
import uuid


# Configure root logger
def setup_logging(level: str = "INFO") -> None:
    """
    Configure application logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request", extra={"request_id": "123"})
    """
    return logging.getLogger(name)


def generate_request_id() -> str:
    """
    Generate a unique request ID for correlation.
    
    Returns:
        UUID string for request tracking
    """
    return str(uuid.uuid4())[:8]


class LogContext:
    """
    Context manager for adding context to log messages.
    
    Useful for adding request-specific information to all logs
    within a request lifecycle.
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        request_id: Optional[str] = None,
        **context
    ):
        self.logger = logger
        self.request_id = request_id or generate_request_id()
        self.context = context
    
    def _format_message(self, message: str) -> str:
        """Add context to log message."""
        ctx_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
        if ctx_str:
            return f"[{self.request_id}] {message} | {ctx_str}"
        return f"[{self.request_id}] {message}"
    
    def debug(self, message: str, **kwargs) -> None:
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        self.logger.error(self._format_message(message), **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        self.logger.exception(self._format_message(message), **kwargs)


# Pre-configured loggers for common modules
api_logger = get_logger("api")
db_logger = get_logger("database")
auth_logger = get_logger("auth")
service_logger = get_logger("service")
