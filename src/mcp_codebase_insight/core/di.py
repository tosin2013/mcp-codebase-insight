"""Dependency Injection Container for MCP Server."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import asyncio
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

from .config import ServerConfig
from .vector_store import VectorStore
from .cache import CacheManager
from .metrics import MetricsManager
from .health import HealthManager
from .documentation import DocumentationManager
from .knowledge import KnowledgeBase
from .tasks import TaskManager
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ComponentContext:
    """Context for managing component lifecycle."""
    initialized: bool = False
    cleanup_tasks: list = field(default_factory=list)
    error: Optional[Exception] = None

@dataclass
class DIContainer:
    """Dependency Injection Container for managing server components."""
    
    config: ServerConfig
    _components: Dict[str, Any] = field(default_factory=dict)
    _contexts: Dict[str, ComponentContext] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize component contexts."""
        self._contexts = {
            "embedding_model": ComponentContext(),
            "vector_store": ComponentContext(),
            "cache_manager": ComponentContext(),
            "metrics_manager": ComponentContext(),
            "health_manager": ComponentContext(),
            "docs_manager": ComponentContext(),
            "knowledge_base": ComponentContext(),
            "task_manager": ComponentContext()
        }
    
    async def initialize_component(self, name: str, factory_func) -> Any:
        """Initialize a component with proper error handling and lifecycle management."""
        context = self._contexts[name]
        if context.initialized:
            return self._components[name]
            
        try:
            component = await factory_func()
            if hasattr(component, 'initialize'):
                await component.initialize()
            
            self._components[name] = component
            context.initialized = True
            
            # Register cleanup if available
            if hasattr(component, 'cleanup'):
                context.cleanup_tasks.append(component.cleanup)
            elif hasattr(component, 'close'):
                context.cleanup_tasks.append(component.close)
                
            return component
            
        except Exception as e:
            context.error = e
            logger.error(f"Failed to initialize {name}: {str(e)}")
            raise
    
    async def get_embedding_model(self) -> SentenceTransformer:
        """Get or create the embedding model."""
        async def factory():
            return SentenceTransformer(self.config.embedding_model)
        return await self.initialize_component("embedding_model", factory)
    
    async def get_vector_store(self) -> VectorStore:
        """Get or create the vector store."""
        async def factory():
            embedding_model = await self.get_embedding_model()
            client = QdrantClient(
                url=self.config.qdrant_url,
                timeout=60.0  # Configurable timeout
            )
            return VectorStore(
                client=client,
                embedder=embedding_model,
                collection_name=self.config.collection_name
            )
        return await self.initialize_component("vector_store", factory)
    
    async def get_cache_manager(self) -> CacheManager:
        """Get or create the cache manager."""
        async def factory():
            return CacheManager(
                memory_size=self.config.memory_cache_size,
                disk_path=self.config.disk_cache_dir
            )
        return await self.initialize_component("cache_manager", factory)
    
    async def get_metrics_manager(self) -> MetricsManager:
        """Get or create the metrics manager."""
        async def factory():
            return MetricsManager(enabled=self.config.metrics_enabled)
        return await self.initialize_component("metrics_manager", factory)
    
    async def get_health_manager(self) -> HealthManager:
        """Get or create the health manager."""
        async def factory():
            metrics = await self.get_metrics_manager()
            cache = await self.get_cache_manager()
            return HealthManager(metrics=metrics, cache=cache)
        return await self.initialize_component("health_manager", factory)
    
    async def get_docs_manager(self) -> DocumentationManager:
        """Get or create the documentation manager."""
        async def factory():
            vector_store = await self.get_vector_store()
            cache = await self.get_cache_manager()
            return DocumentationManager(
                vector_store=vector_store,
                cache=cache,
                docs_dir=self.config.docs_cache_dir
            )
        return await self.initialize_component("docs_manager", factory)
    
    async def get_knowledge_base(self) -> KnowledgeBase:
        """Get or create the knowledge base."""
        async def factory():
            vector_store = await self.get_vector_store()
            cache = await self.get_cache_manager()
            return KnowledgeBase(
                vector_store=vector_store,
                cache=cache,
                storage_dir=self.config.kb_storage_dir
            )
        return await self.initialize_component("knowledge_base", factory)
    
    async def get_task_manager(self) -> TaskManager:
        """Get or create the task manager."""
        async def factory():
            kb = await self.get_knowledge_base()
            docs = await self.get_docs_manager()
            return TaskManager(
                knowledge_base=kb,
                docs_manager=docs,
                max_tasks=100  # Configurable
            )
        return await self.initialize_component("task_manager", factory)
    
    async def cleanup(self):
        """Clean up all components in reverse initialization order."""
        for name, context in reversed(list(self._contexts.items())):
            if context.initialized:
                try:
                    for cleanup_task in reversed(context.cleanup_tasks):
                        await cleanup_task()
                    context.initialized = False
                except Exception as e:
                    logger.error(f"Error cleaning up {name}: {str(e)}")
                    
        self._components.clear() 