"""Core components for MCP server."""

from .adr import ADRManager, ADRStatus
from .cache import CacheManager
from .config import ServerConfig
from .debug import DebugSystem, IssueType, IssueStatus
from .documentation import DocumentationManager
from .embeddings import EmbeddingProvider
from .errors import (
    ErrorCode,
    SystemError,
    ValidationError,
    TaskError,
    handle_error,
    error_to_dict
)
from .health import HealthMonitor, HealthStatus
from .knowledge import KnowledgeBase, PatternType
from .metrics import MetricsCollector
from .prompts import PromptManager, PromptType, PromptContext
from .tasks import TaskManager, TaskType, TaskStatus, TaskPriority
from .vector_store import VectorStore, SearchResult

__all__ = [
    # ADR management
    "ADRManager",
    "ADRStatus",
    
    # Caching
    "CacheManager",
    
    # Configuration
    "ServerConfig",
    
    # Debugging
    "DebugSystem",
    "IssueType",
    "IssueStatus",
    
    # Documentation
    "DocumentationManager",
    
    # Embeddings
    "EmbeddingProvider",
    
    # Error handling
    "ErrorCode",
    "SystemError",
    "ValidationError",
    "TaskError",
    "handle_error",
    "error_to_dict",
    
    # Health monitoring
    "HealthMonitor",
    "HealthStatus",
    
    # Knowledge base
    "KnowledgeBase",
    "PatternType",
    
    # Metrics
    "MetricsCollector",
    
    # Prompts
    "PromptManager",
    "PromptType",
    "PromptContext",
    
    # Tasks
    "TaskManager",
    "TaskType",
    "TaskStatus",
    "TaskPriority",
    
    # Vector store
    "VectorStore",
    "SearchResult"
]
