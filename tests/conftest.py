"""Test configuration and fixtures."""

import asyncio
import os
from pathlib import Path
import pytest
import tempfile
from typing import AsyncGenerator, Generator

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from src.mcp_server_qdrant.core.config import ServerConfig
from src.mcp_server_qdrant.core.embeddings import EmbeddingProvider
from src.mcp_server_qdrant.core.vector_store import VectorStore
from src.mcp_server_qdrant.core.knowledge import KnowledgeBase
from src.mcp_server_qdrant.core.cache import CacheManager
from src.mcp_server_qdrant.core.metrics import MetricsCollector
from src.mcp_server_qdrant.core.health import HealthMonitor
from src.mcp_server_qdrant.core.adr import ADRManager
from src.mcp_server_qdrant.core.debug import DebugSystem
from src.mcp_server_qdrant.core.documentation import DocumentationManager
from src.mcp_server_qdrant.core.prompts import PromptManager
from src.mcp_server_qdrant.core.tasks import TaskManager

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp:
        yield Path(temp)

@pytest.fixture
def test_config(temp_dir: Path) -> ServerConfig:
    """Create test configuration."""
    return ServerConfig(
        qdrant_url="http://localhost:6333",
        collection_name="test_collection",
        host="127.0.0.1",
        port=3000,
        log_level="DEBUG",
        docs_cache_dir=temp_dir / "references",
        kb_storage_dir=temp_dir / "knowledge"
    )

@pytest.fixture
async def qdrant_client() -> AsyncGenerator[QdrantClient, None]:
    """Create Qdrant client."""
    client = QdrantClient(
        url="http://localhost:6333",
        timeout=5.0
    )
    yield client
    await client.close()

@pytest.fixture
async def embedding_provider(test_config: ServerConfig) -> AsyncGenerator[EmbeddingProvider, None]:
    """Create embedding provider."""
    provider = await EmbeddingProvider.create(test_config)
    yield provider

@pytest.fixture
async def vector_store(
    test_config: ServerConfig,
    qdrant_client: QdrantClient,
    embedding_provider: EmbeddingProvider
) -> AsyncGenerator[VectorStore, None]:
    """Create vector store."""
    store = VectorStore(
        client=qdrant_client,
        embedder=embedding_provider,
        collection_name=test_config.collection_name
    )
    await store.initialize()
    yield store
    await store.close()

@pytest.fixture
async def cache_manager(test_config: ServerConfig) -> AsyncGenerator[CacheManager, None]:
    """Create cache manager."""
    manager = CacheManager(test_config)
    yield manager
    await manager.stop()

@pytest.fixture
async def metrics_collector(test_config: ServerConfig) -> AsyncGenerator[MetricsCollector, None]:
    """Create metrics collector."""
    collector = MetricsCollector(test_config)
    yield collector
    await collector.stop()

@pytest.fixture
async def health_monitor(test_config: ServerConfig) -> AsyncGenerator[HealthMonitor, None]:
    """Create health monitor."""
    monitor = HealthMonitor(test_config)
    yield monitor
    await monitor.stop()

@pytest.fixture
async def knowledge_base(
    test_config: ServerConfig,
    vector_store: VectorStore
) -> AsyncGenerator[KnowledgeBase, None]:
    """Create knowledge base."""
    kb = KnowledgeBase(test_config, vector_store)
    yield kb

@pytest.fixture
async def adr_manager(test_config: ServerConfig) -> AsyncGenerator[ADRManager, None]:
    """Create ADR manager."""
    manager = ADRManager(test_config)
    yield manager

@pytest.fixture
async def debug_system(test_config: ServerConfig) -> AsyncGenerator[DebugSystem, None]:
    """Create debug system."""
    system = DebugSystem(test_config)
    yield system

@pytest.fixture
async def doc_manager(test_config: ServerConfig) -> AsyncGenerator[DocumentationManager, None]:
    """Create documentation manager."""
    manager = DocumentationManager(test_config)
    yield manager

@pytest.fixture
async def prompt_manager(
    test_config: ServerConfig,
    knowledge_base: KnowledgeBase
) -> AsyncGenerator[PromptManager, None]:
    """Create prompt manager."""
    manager = PromptManager(test_config, knowledge_base)
    yield manager

@pytest.fixture
async def task_manager(
    test_config: ServerConfig,
    adr_manager: ADRManager,
    debug_system: DebugSystem,
    doc_manager: DocumentationManager,
    knowledge_base: KnowledgeBase,
    prompt_manager: PromptManager
) -> AsyncGenerator[TaskManager, None]:
    """Create task manager."""
    manager = TaskManager(
        config=test_config,
        adr_manager=adr_manager,
        debug_system=debug_system,
        doc_manager=doc_manager,
        knowledge_base=knowledge_base,
        prompt_manager=prompt_manager
    )
    yield manager
