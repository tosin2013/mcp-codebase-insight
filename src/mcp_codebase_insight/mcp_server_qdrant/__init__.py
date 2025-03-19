"""MCP server for codebase analysis."""

__version__ = "0.1.0"

from .core.config import ServerConfig
from .core.adr import ADRManager, ADRStatus
from .core.debug import DebugSystem, IssueType, IssueStatus
from .core.documentation import DocumentationManager
from .core.knowledge import KnowledgeBase, PatternType
from .core.prompts import PromptManager, PromptType, PromptContext
from .core.tasks import TaskManager, TaskType, TaskStatus, TaskPriority
from .core.metrics import MetricsCollector
from .core.health import HealthMonitor, HealthStatus
from .core.cache import CacheManager
from .core.embeddings import EmbeddingProvider
from .core.vector_store import VectorStore, SearchResult
from .core.errors import (
    ErrorCode,
    SystemError,
    ValidationError,
    TaskError,
    handle_error,
    error_to_dict
)
from .server import CodebaseAnalysisServer

__all__ = [
    # Version
    "__version__",
    
    # Server
    "CodebaseAnalysisServer",
    "ServerConfig",
    
    # Core components
    "ADRManager",
    "ADRStatus",
    "DebugSystem",
    "IssueType",
    "IssueStatus",
    "DocumentationManager",
    "KnowledgeBase",
    "PatternType",
    "PromptManager",
    "PromptType",
    "PromptContext",
    "TaskManager",
    "TaskType",
    "TaskStatus",
    "TaskPriority",
    "MetricsCollector",
    "HealthMonitor",
    "HealthStatus",
    "CacheManager",
    "EmbeddingProvider",
    "VectorStore",
    "SearchResult",
    
    # Error handling
    "ErrorCode",
    "SystemError",
    "ValidationError",
    "TaskError",
    "handle_error",
    "error_to_dict"
]
