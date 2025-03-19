from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import traceback

class ErrorCode(Enum):
    """Error codes for system errors."""
    # Infrastructure errors
    VECTOR_STORE_ERROR = "vector_store_error"
    CACHE_ERROR = "cache_error"
    CONFIG_ERROR = "config_error"
    STORAGE_ERROR = "storage_error"
    
    # Task errors
    TASK_NOT_FOUND = "task_not_found"
    TASK_FAILED = "task_failed"
    STEP_FAILED = "step_failed"
    INVALID_TASK_TYPE = "invalid_task_type"
    
    # Analysis errors
    ANALYSIS_ERROR = "analysis_error"
    PATTERN_NOT_FOUND = "pattern_not_found"
    INVALID_PATTERN = "invalid_pattern"
    
    # ADR errors
    ADR_NOT_FOUND = "adr_not_found"
    ADR_CREATION_FAILED = "adr_creation_failed"
    ADR_UPDATE_FAILED = "adr_update_failed"
    
    # Debug errors
    DEBUG_SESSION_NOT_FOUND = "debug_session_not_found"
    DEBUG_STEP_FAILED = "debug_step_failed"
    
    # Documentation errors
    DOC_FETCH_FAILED = "doc_fetch_failed"
    DOC_STORE_FAILED = "doc_store_failed"
    DOC_NOT_FOUND = "doc_not_found"
    
    # Knowledge base errors
    KB_STORE_ERROR = "kb_store_error"
    KB_SEARCH_ERROR = "kb_search_error"
    KB_UPDATE_ERROR = "kb_update_error"
    
    # Prompt errors
    PROMPT_GENERATION_FAILED = "prompt_generation_failed"
    PROMPT_TEMPLATE_NOT_FOUND = "prompt_template_not_found"
    INVALID_PROMPT_CONTEXT = "invalid_prompt_context"
    
    # General errors
    VALIDATION_ERROR = "validation_error"
    INTERNAL_ERROR = "internal_error"
    NOT_IMPLEMENTED = "not_implemented"
    TIMEOUT = "timeout"

@dataclass
class ErrorContext:
    """Context information for errors."""
    component: str
    operation: str
    input_data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    step_id: Optional[str] = None
    timestamp: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "operation": self.operation,
            "input_data": self.input_data,
            "task_id": self.task_id,
            "step_id": self.step_id,
            "timestamp": self.timestamp.isoformat()
        }

class SystemError(Exception):
    """Base class for system errors."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        context: ErrorContext,
        cause: Optional[Exception] = None
    ):
        """Initialize error."""
        self.code = code
        self.message = message
        self.context = context
        self.cause = cause
        self.traceback = traceback.format_exc() if cause else None
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code.value,
            "message": self.message,
            "context": self.context.to_dict(),
            "cause": str(self.cause) if self.cause else None,
            "traceback": self.traceback
        }

class ValidationError(SystemError):
    """Error for validation failures."""
    
    def __init__(
        self,
        message: str,
        context: ErrorContext,
        validation_errors: Dict[str, str]
    ):
        """Initialize validation error."""
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            context=context
        )
        self.validation_errors = validation_errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        error_dict = super().to_dict()
        error_dict["validation_errors"] = self.validation_errors
        return error_dict

class TaskError(SystemError):
    """Error for task execution failures."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        context: ErrorContext,
        task_id: str,
        step_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """Initialize task error."""
        context.task_id = task_id
        context.step_id = step_id
        super().__init__(code, message, context, cause)

def handle_error(error: Exception, context: ErrorContext) -> SystemError:
    """Convert exception to system error."""
    if isinstance(error, SystemError):
        return error
    
    # Map common exceptions to system errors
    if isinstance(error, ValueError):
        return SystemError(
            code=ErrorCode.VALIDATION_ERROR,
            message=str(error),
            context=context,
            cause=error
        )
    elif isinstance(error, NotImplementedError):
        return SystemError(
            code=ErrorCode.NOT_IMPLEMENTED,
            message=str(error),
            context=context,
            cause=error
        )
    elif isinstance(error, TimeoutError):
        return SystemError(
            code=ErrorCode.TIMEOUT,
            message=str(error),
            context=context,
            cause=error
        )
    else:
        return SystemError(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(error),
            context=context,
            cause=error
        )

def error_to_dict(error: Exception) -> Dict[str, Any]:
    """Convert error to dictionary."""
    if isinstance(error, SystemError):
        return error.to_dict()
    else:
        return {
            "code": ErrorCode.INTERNAL_ERROR.value,
            "message": str(error),
            "traceback": traceback.format_exc()
        }
