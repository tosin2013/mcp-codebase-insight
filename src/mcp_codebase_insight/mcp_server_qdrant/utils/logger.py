import logging
import sys
from typing import Any, Dict, Optional
import structlog
from structlog.types import Processor

def setup_logging(level: str = "INFO") -> None:
    """Setup structured logging configuration."""
    # Set log level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Configure structlog processors
    shared_processors: list[Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if level == "DEBUG":
        # Add call location in debug mode
        shared_processors.append(structlog.processors.CallsiteParameterAdder(
            parameters={
                "func_name": structlog.processors.CallsiteParameter.FUNC_NAME,
                "lineno": structlog.processors.CallsiteParameter.LINENO,
            }
        ))

    # Configure structlog
    structlog.configure(
        processors=[
            *shared_processors,
            # Format for console output
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback
            )
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance with the given name."""
    return structlog.get_logger(name)

class LogContext:
    """Context manager for adding temporary context to logs."""
    
    def __init__(
        self,
        logger: structlog.BoundLogger,
        **kwargs: Any
    ):
        """Initialize log context."""
        self.logger = logger
        self.temp_context = kwargs
        self.previous_context: Dict[str, Any] = {}

    def __enter__(self) -> structlog.BoundLogger:
        """Add temporary context."""
        # Save current context
        for key in self.temp_context:
            if hasattr(self.logger, key):
                self.previous_context[key] = getattr(self.logger, key)
        
        # Add new context
        return self.logger.bind(**self.temp_context)

    def __exit__(self, *args: Any) -> None:
        """Restore previous context."""
        # Remove temporary context
        self.logger = self.logger.unbind(*self.temp_context.keys())
        
        # Restore previous context
        if self.previous_context:
            self.logger = self.logger.bind(**self.previous_context)

class TaskLogger:
    """Logger with task context."""
    
    def __init__(
        self,
        logger: structlog.BoundLogger,
        task_id: str,
        task_type: str
    ):
        """Initialize task logger."""
        self.logger = logger.bind(task_id=task_id, task_type=task_type)

    def step_context(self, step_id: str) -> LogContext:
        """Get context manager for step logging."""
        return LogContext(self.logger, step_id=step_id)

    def debug(self, event: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(event, **kwargs)

    def exception(
        self,
        event: str,
        exc_info: Optional[BaseException] = None,
        **kwargs: Any
    ) -> None:
        """Log exception with traceback."""
        self.logger.exception(event, exc_info=exc_info, **kwargs)

def get_task_logger(
    name: str,
    task_id: str,
    task_type: str
) -> TaskLogger:
    """Get a logger instance with task context."""
    logger = get_logger(name)
    return TaskLogger(logger, task_id, task_type)
