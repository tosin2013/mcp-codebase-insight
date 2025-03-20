"""Structured logging module."""

import logging
import sys
from typing import Any, Dict, Optional

import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class Logger:
    """Structured logger."""
    
    def __init__(
        self,
        name: str,
        level: str = "INFO",
        extra: Optional[Dict[str, Any]] = None
    ):
        """Initialize logger."""
        # Set log level
        log_level = getattr(logging, level.upper())
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=log_level,
        )
        
        # Create logger
        self.logger = structlog.get_logger(name)
        self.extra = extra or {}
    
    def bind(self, **kwargs) -> "Logger":
        """Create new logger with additional context."""
        extra = {**self.extra, **kwargs}
        return Logger(
            name=self.logger.name,
            level=logging.getLevelName(self.logger.level),
            extra=extra
        )
    
    def debug(self, event: str, **kwargs):
        """Log debug message."""
        self.logger.debug(
            event,
            **{**self.extra, **kwargs}
        )
    
    def info(self, event: str, **kwargs):
        """Log info message."""
        self.logger.info(
            event,
            **{**self.extra, **kwargs}
        )
    
    def warning(self, event: str, **kwargs):
        """Log warning message."""
        self.logger.warning(
            event,
            **{**self.extra, **kwargs}
        )
    
    def error(self, event: str, **kwargs):
        """Log error message."""
        self.logger.error(
            event,
            **{**self.extra, **kwargs}
        )
    
    def exception(self, event: str, exc_info: bool = True, **kwargs):
        """Log exception message."""
        self.logger.exception(
            event,
            exc_info=exc_info,
            **{**self.extra, **kwargs}
        )
    
    def critical(self, event: str, **kwargs):
        """Log critical message."""
        self.logger.critical(
            event,
            **{**self.extra, **kwargs}
        )

def get_logger(
    name: str,
    level: str = "INFO",
    extra: Optional[Dict[str, Any]] = None
) -> Logger:
    """Get logger instance."""
    return Logger(name, level, extra)

# Default logger
logger = get_logger("mcp_codebase_insight")
