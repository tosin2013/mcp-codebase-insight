"""Server state management."""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any, Set
import asyncio
from contextlib import AsyncExitStack
import sys
import threading
from datetime import datetime
import logging
import uuid
from enum import Enum

from ..utils.logger import get_logger
from .config import ServerConfig
from .di import DIContainer
from .task_tracker import TaskTracker

logger = get_logger(__name__)

class ComponentStatus(Enum):
    """Component initialization status."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    FAILED = "failed"
    CLEANING = "cleaning"
    CLEANED = "cleaned"

@dataclass
class ComponentState:
    """State tracking for a server component."""
    status: ComponentStatus = ComponentStatus.UNINITIALIZED
    error: Optional[str] = None
    instance: Any = None
    last_update: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class ServerState:
    """Global server state management."""
    
    def __init__(self):
        """Initialize server state."""
        self._init_lock = asyncio.Lock()
        self._cleanup_lock = asyncio.Lock()
        self.initialized = False
        self.config: Optional[ServerConfig] = None
        self._components: Dict[str, ComponentState] = {}
        self._cleanup_handlers: List[asyncio.Task] = []
        self._task_tracker = TaskTracker()
        self._instance_id = str(uuid.uuid4())
        logger.info(f"Created ServerState instance {self._instance_id}")
    
    def register_component(self, name: str, instance: Any = None) -> None:
        """Register a new component."""
        if name not in self._components:
            component_state = ComponentState()
            if instance:
                component_state.instance = instance
            self._components[name] = component_state
            logger.debug(f"Registered component: {name}")
    
    def update_component_status(
        self, 
        name: str, 
        status: ComponentStatus, 
        error: Optional[str] = None,
        instance: Any = None
    ) -> None:
        """Update component status."""
        if name not in self._components:
            self.register_component(name)
        
        component = self._components[name]
        component.status = status
        component.error = error
        component.last_update = datetime.utcnow()
        
        if instance is not None:
            component.instance = instance
        
        if status == ComponentStatus.FAILED:
            component.retry_count += 1
        
        logger.debug(
            f"Component {name} status updated to {status}"
            f"{f' (error: {error})' if error else ''}"
        )
    
    def get_component(self, name: str) -> Any:
        """Get component instance."""
        if name not in self._components:
            logger.warning(f"Component {name} not registered")
            return None
            
        component = self._components[name]
        if component.status != ComponentStatus.INITIALIZED:
            logger.warning(f"Component {name} not initialized (status: {component.status.value})")
            return None
            
        return component.instance
    
    def register_background_task(self, task: asyncio.Task) -> None:
        """Register a background task for tracking and cleanup."""
        self._task_tracker.track_task(task)
        logger.debug(f"Registered background task: {task.get_name()}")
    
    async def cancel_background_tasks(self) -> None:
        """Cancel all tracked background tasks."""
        await self._task_tracker.cancel_all_tasks()
    
    async def cleanup(self) -> None:
        """Cleanup server components."""
        async with self._cleanup_lock:
            if not self.initialized:
                logger.warning("Server not initialized, nothing to clean up")
                return
            
            logger.info(f"Beginning cleanup for instance {self._instance_id}")
            
            # First, cancel any background tasks
            await self.cancel_background_tasks()
            
            # Clean up components in reverse order
            components = list(self._components.keys())
            components.reverse()
            
            for component in components:
                self.update_component_status(component, ComponentStatus.CLEANING)
                try:
                    # Component-specific cleanup logic here
                    comp_instance = self._components[component].instance
                    if comp_instance and hasattr(comp_instance, 'cleanup'):
                        await comp_instance.cleanup()
                    
                    self.update_component_status(component, ComponentStatus.CLEANED)
                except Exception as e:
                    error_msg = f"Error cleaning up {component}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.update_component_status(
                        component,
                        ComponentStatus.FAILED,
                        error_msg
                    )
            
            # Cancel any remaining cleanup handlers
            for task in self._cleanup_handlers:
                if not task.done():
                    task.cancel()
            
            self.initialized = False
            logger.info(f"Server instance {self._instance_id} cleanup completed")
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get status of all components."""
        return {
            name: {
                "status": comp.status.value,
                "error": comp.error,
                "last_update": comp.last_update.isoformat(),
                "retry_count": comp.retry_count,
                "instance_id": comp.instance_id
            }
            for name, comp in self._components.items()
        }
    
    def register_cleanup_handler(self, task: asyncio.Task) -> None:
        """Register a cleanup handler task."""
        self._cleanup_handlers.append(task)
        logger.debug(f"Registered cleanup handler: {task.get_name()}")
    
    @property
    def instance_id(self) -> str:
        """Get the unique instance ID of this server state."""
        return self._instance_id
    
    def list_components(self) -> List[str]:
        """List all registered components."""
        return list(self._components.keys())
    
    def get_active_tasks(self) -> Set[asyncio.Task]:
        """Get all currently active tasks."""
        return self._task_tracker.get_active_tasks()
    
    def get_task_count(self) -> int:
        """Get the number of currently tracked tasks."""
        return self._task_tracker.get_task_count()

    async def initialize(self) -> None:
        """Initialize server components."""
        async with self._init_lock:
            if self.initialized:
                logger.warning("Server already initialized")
                return
            
            logger.info(f"Beginning initialization for instance {self._instance_id}")
            
            try:
                # Initialize components in order
                components = [
                    "database",
                    "vector_store",
                    "task_manager",
                    "analysis_engine",
                    "adr_manager",
                    "knowledge_base"
                ]
                
                for component in components:
                    self.update_component_status(component, ComponentStatus.INITIALIZING)
                    try:
                        # Component-specific initialization logic here
                        # await self._initialize_component(component)
                        
                        # For now, let's just mark them as initialized
                        # In a real implementation, you'd create and store the actual component instances
                        
                        # For the vector_store component, create a real instance
                        if component == "vector_store":
                            from .vector_store import VectorStore
                            from .embeddings import SentenceTransformerEmbedding
                            
                            # If config is available, use it to configure the vector store
                            if self.config:
                                embedder = SentenceTransformerEmbedding(self.config.embedding_model)
                                vector_store = VectorStore(
                                    url=self.config.qdrant_url,
                                    embedder=embedder,
                                    collection_name=self.config.collection_name
                                )
                                await vector_store.initialize()
                                self.update_component_status(
                                    "vector_store", 
                                    ComponentStatus.INITIALIZED,
                                    instance=vector_store
                                )
                        
                        # For the adr_manager component
                        elif component == "adr_manager":
                            from .adr import ADRManager
                            if self.config:
                                adr_manager = ADRManager(self.config)
                                await adr_manager.initialize()
                                self.update_component_status(
                                    "adr_manager",
                                    ComponentStatus.INITIALIZED,
                                    instance=adr_manager
                                )
                        
                        # For the knowledge_base component
                        elif component == "knowledge_base":
                            from .knowledge import KnowledgeBase
                            if self.config:
                                # Get vector_store if available
                                vector_store = self.get_component("vector_store")
                                if vector_store:
                                    kb = KnowledgeBase(self.config, vector_store)
                                    await kb.initialize()
                                    self.update_component_status(
                                        "knowledge_base",
                                        ComponentStatus.INITIALIZED,
                                        instance=kb
                                    )
                                else:
                                    error_msg = "Vector store not initialized, cannot initialize knowledge base"
                                    logger.error(error_msg)
                                    self.update_component_status(
                                        component,
                                        ComponentStatus.FAILED,
                                        error=error_msg
                                    )
                        
                        # For task_manager component
                        elif component == "task_manager":
                            from .tasks import TaskManager
                            if self.config:
                                task_manager = TaskManager(self.config)
                                await task_manager.initialize()
                                self.update_component_status(
                                    "task_manager",
                                    ComponentStatus.INITIALIZED,
                                    instance=task_manager
                                )
                        
                        # For database component (placeholder)
                        elif component == "database":
                            # Mock implementation for database
                            self.update_component_status(
                                "database",
                                ComponentStatus.INITIALIZED,
                                instance={"status": "mocked"}
                            )
                        
                        # For analysis_engine component (placeholder)
                        elif component == "analysis_engine":
                            # Mock implementation for analysis engine
                            self.update_component_status(
                                "analysis_engine",
                                ComponentStatus.INITIALIZED,
                                instance={"status": "mocked"}
                            )
                            
                    except Exception as e:
                        error_msg = f"Failed to initialize {component}: {str(e)}"
                        logger.error(error_msg, exc_info=True)
                        self.update_component_status(
                            component, 
                            ComponentStatus.FAILED,
                            error=error_msg
                        )
                
                # Set server as initialized if all critical components are initialized
                critical_components = ["vector_store", "task_manager"]
                all_critical_initialized = all(
                    self._components.get(c) and 
                    self._components[c].status == ComponentStatus.INITIALIZED 
                    for c in critical_components
                )
                
                if all_critical_initialized:
                    self.initialized = True
                    logger.info(f"Server instance {self._instance_id} initialized successfully")
                else:
                    logger.warning(
                        f"Server instance {self._instance_id} partially initialized "
                        f"(some critical components failed)"
                    )
                
            except Exception as e:
                error_msg = f"Failed to initialize server: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise 