"""Custom exceptions for error handling."""

class CodebaseInsightError(Exception):
    """Base exception for all codebase insight errors."""
    pass

class ConfigurationError(CodebaseInsightError):
    """Raised when there is a configuration error."""
    pass

class VectorStoreError(CodebaseInsightError):
    """Raised when there is an error with vector store operations."""
    pass

class DocumentationError(CodebaseInsightError):
    """Raised when there is an error with documentation operations."""
    pass

class ADRError(CodebaseInsightError):
    """Raised when there is an error with ADR operations."""
    pass

class KnowledgeBaseError(CodebaseInsightError):
    """Raised when there is an error with knowledge base operations."""
    pass

class TaskError(CodebaseInsightError):
    """Raised when there is an error with task operations."""
    pass

class ValidationError(CodebaseInsightError):
    """Raised when there is a validation error."""
    pass

class ResourceNotFoundError(CodebaseInsightError):
    """Raised when a requested resource is not found."""
    pass

class OperationNotSupportedError(CodebaseInsightError):
    """Raised when an operation is not supported."""
    pass
