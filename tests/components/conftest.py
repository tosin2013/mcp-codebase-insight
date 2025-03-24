"""
Component Test Fixture Configuration.

This file defines fixtures specifically for component tests that might have different
scope requirements than the main test fixtures.
"""
import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
import uuid
from typing import Dict

# Import required components
from src.mcp_codebase_insight.core.config import ServerConfig
from src.mcp_codebase_insight.core.vector_store import VectorStore
from src.mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding
from src.mcp_codebase_insight.core.knowledge import KnowledgeBase
from src.mcp_codebase_insight.core.tasks import TaskManager

@pytest.fixture
def test_config():
    """Create a server configuration for tests.
    
    This is an alias for test_server_config that allows component tests to use
    their expected fixture name.
    """
    config = ServerConfig(
        host="localhost",
        port=8000,
        log_level="DEBUG",
        qdrant_url="http://localhost:6333",
        docs_cache_dir=Path(".test_cache") / "docs",
        adr_dir=Path(".test_cache") / "docs/adrs",
        kb_storage_dir=Path(".test_cache") / "knowledge",
        embedding_model="all-MiniLM-L6-v2",
        collection_name=f"test_collection_{uuid.uuid4().hex[:8]}",
        debug_mode=True,
        metrics_enabled=False,
        cache_enabled=True,
        memory_cache_size=1000,
        disk_cache_dir=Path(".test_cache") / "cache"
    )
    return config

@pytest.fixture
def test_metadata() -> Dict:
    """Standard test metadata for consistency across tests."""
    return {
        "type": "code",
        "language": "python",
        "title": "Test Code",
        "description": "Test code snippet for vector store testing",
        "tags": ["test", "vector"]
    }

@pytest_asyncio.fixture
async def embedder():
    """Create an embedder for tests."""
    return SentenceTransformerEmbedding()

@pytest_asyncio.fixture
async def vector_store(test_config, embedder):
    """Create a vector store for tests."""
    store = VectorStore(test_config.qdrant_url, embedder)
    await store.initialize()
    yield store
    await store.cleanup()

@pytest_asyncio.fixture
async def task_manager(test_config):
    """Create a task manager for tests."""
    manager = TaskManager(test_config)
    await manager.initialize()
    yield manager
    await manager.cleanup()

@pytest.fixture
def test_code():
    """Provide sample code for testing task-related functionality."""
    return """
def example_function():
    \"\"\"This is a test function for task manager tests.\"\"\"
    return "Hello, world!"

class TestClass:
    def __init__(self):
        self.value = 42
        
    def method(self):
        return self.value
"""

@pytest_asyncio.fixture
async def knowledge_base(test_config, vector_store):
    """Create a knowledge base for tests."""
    kb = KnowledgeBase(test_config, vector_store)
    await kb.initialize()
    yield kb
    await kb.cleanup()
