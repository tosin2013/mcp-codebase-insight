"""Logging configuration."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import structlog

def get_logger(name: str, log_level: Optional[str] = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    level = log_level or os.getenv("LOG_LEVEL", "INFO")
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    debug_dir = log_dir / "debug"
    log_dir.mkdir(exist_ok=True)
    debug_dir.mkdir(exist_ok=True)

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Add file handler for debug logs
    if level == "DEBUG":
        debug_handler = logging.FileHandler(
            debug_dir / f"{name.replace('.', '_')}.log"
        )
        debug_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(debug_handler)

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

    return structlog.get_logger(name)
