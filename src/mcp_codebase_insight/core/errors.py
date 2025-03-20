"""Error handling module."""

from enum import Enum
from typing import Any, Dict, Optional

class ErrorCode(str, Enum):
    """Error code enumeration."""
    
    # General errors
    INTERNAL_ERROR = "internal_error"
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    VALIDATION_ERROR = "validation_error"
    
    # Component-specific errors
    VECTOR_STORE_ERROR = "vector_store_error"
    EMBEDDING_ERROR = "embedding_error"
    CACHE_ERROR = "cache_error"
    TASK_ERROR = "task_error"
    ADR_ERROR = "adr_error"
    DOCUMENTATION_ERROR = "documentation_error"
    DEBUG_ERROR = "debug_error"
    PROMPT_ERROR = "prompt_error"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    
    # Authentication/Authorization errors
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    TOKEN_EXPIRED = "token_expired"
    
    # Rate limiting errors
    RATE_LIMITED = "rate_limited"
    QUOTA_EXCEEDED = "quota_exceeded"
    
    # Configuration errors
    CONFIG_ERROR = "config_error"
    MISSING_CONFIG = "missing_config"
    INVALID_CONFIG = "invalid_config"

class BaseError(Exception):
    """Base error class."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }

class InternalError(BaseError):
    """Internal server error."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.INTERNAL_ERROR, message, details)

class InvalidRequestError(BaseError):
    """Invalid request error."""
    
    def __init__(
        self,
        message: str = "Invalid request",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.INVALID_REQUEST, message, details)

class NotFoundError(BaseError):
    """Not found error."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.NOT_FOUND, message, details)

class AlreadyExistsError(BaseError):
    """Already exists error."""
    
    def __init__(
        self,
        message: str = "Resource already exists",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.ALREADY_EXISTS, message, details)

class ValidationError(BaseError):
    """Validation error."""
    
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.VALIDATION_ERROR, message, details)

class VectorStoreError(BaseError):
    """Vector store error."""
    
    def __init__(
        self,
        message: str = "Vector store error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.VECTOR_STORE_ERROR, message, details)

class EmbeddingError(BaseError):
    """Embedding error."""
    
    def __init__(
        self,
        message: str = "Embedding error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.EMBEDDING_ERROR, message, details)

class CacheError(BaseError):
    """Cache error."""
    
    def __init__(
        self,
        message: str = "Cache error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.CACHE_ERROR, message, details)

class TaskError(BaseError):
    """Task error."""
    
    def __init__(
        self,
        message: str = "Task error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.TASK_ERROR, message, details)

class ADRError(BaseError):
    """ADR error."""
    
    def __init__(
        self,
        message: str = "ADR error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.ADR_ERROR, message, details)

class DocumentationError(BaseError):
    """Documentation error."""
    
    def __init__(
        self,
        message: str = "Documentation error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.DOCUMENTATION_ERROR, message, details)

class DebugError(BaseError):
    """Debug error."""
    
    def __init__(
        self,
        message: str = "Debug error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.DEBUG_ERROR, message, details)

class PromptError(BaseError):
    """Prompt error."""
    
    def __init__(
        self,
        message: str = "Prompt error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.PROMPT_ERROR, message, details)

class ConfigError(BaseError):
    """Configuration error."""
    
    def __init__(
        self,
        message: str = "Configuration error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.CONFIG_ERROR, message, details)

class UnauthorizedError(BaseError):
    """Unauthorized error."""
    
    def __init__(
        self,
        message: str = "Unauthorized",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.UNAUTHORIZED, message, details)

class ForbiddenError(BaseError):
    """Forbidden error."""
    
    def __init__(
        self,
        message: str = "Forbidden",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.FORBIDDEN, message, details)

class RateLimitedError(BaseError):
    """Rate limited error."""
    
    def __init__(
        self,
        message: str = "Rate limited",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.RATE_LIMITED, message, details)

class ResourceNotFoundError(BaseError):
    """Resource not found error."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.RESOURCE_NOT_FOUND, message, details)

class ProcessingError(BaseError):
    """Processing error."""
    
    def __init__(
        self,
        message: str = "Processing error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(ErrorCode.INTERNAL_ERROR, message, details)

def handle_error(error: Exception) -> Dict[str, Any]:
    """Convert error to API response format."""
    if isinstance(error, BaseError):
        return error.to_dict()
        
    return {
        "code": ErrorCode.INTERNAL_ERROR,
        "message": str(error),
        "details": {}
    }
