"""Test configuration and fixtures."""

import os
import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

from qdrant_client import QdrantClient
from fastapi.testclient import TestClient

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.server import CodebaseAnalysisServer

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def temp_dir(tmp_path: Path) -> Path:
    """Create temporary directory for test files."""
    return tmp_path

@pytest.fixture
async def test_config(temp_dir: Path) -> ServerConfig:
    """Create test configuration."""
    return ServerConfig(
        host="127.0.0.1",
        port=3000,
        log_level="DEBUG",
        qdrant_url="http://localhost:6333",
        docs_cache_dir=temp_dir / "docs",
        adr_dir=temp_dir / "docs/adrs",
        kb_storage_dir=temp_dir / "knowledge",
        disk_cache_dir=temp_dir / "cache"
    )

@pytest.fixture
async def qdrant_client() -> AsyncGenerator[QdrantClient, None]:
    """Create Qdrant client for tests."""
    client = QdrantClient(url="http://localhost:6333")
    yield client
    # Clean up collections after tests
    collections = client.get_collections().collections
    for collection in collections:
        client.delete_collection(collection.name)

@pytest.fixture
async def test_server(test_config: ServerConfig) -> AsyncGenerator[CodebaseAnalysisServer, None]:
    """Create test server instance."""
    server = CodebaseAnalysisServer(test_config)
    try:
        # Clean up any existing test data
        if test_config.kb_storage_dir.exists():
            import shutil
            shutil.rmtree(test_config.kb_storage_dir)
        if test_config.docs_cache_dir.exists():
            import shutil
            shutil.rmtree(test_config.docs_cache_dir)
        
        # Create necessary directories
        test_config.kb_storage_dir.mkdir(parents=True, exist_ok=True)
        test_config.docs_cache_dir.mkdir(parents=True, exist_ok=True)
        test_config.adr_dir.mkdir(parents=True, exist_ok=True)
        test_config.disk_cache_dir.mkdir(parents=True, exist_ok=True)
        (test_config.docs_cache_dir / "tasks").mkdir(parents=True, exist_ok=True)
        (test_config.docs_cache_dir / "debug").mkdir(parents=True, exist_ok=True)
        
        await server.start()
        # Wait for server components to initialize
        await asyncio.sleep(1)  # Give components time to start
        yield server
    finally:
        await server.stop()
        # Clean up test data
        if test_config.kb_storage_dir.exists():
            import shutil
            shutil.rmtree(test_config.kb_storage_dir)
        if test_config.docs_cache_dir.exists():
            import shutil
            shutil.rmtree(test_config.docs_cache_dir)

@pytest.fixture
def test_client(test_server: CodebaseAnalysisServer) -> TestClient:
    """Create test client."""
    return TestClient(test_server.app)

@pytest.fixture
def test_code() -> str:
    """Sample code for testing."""
    return """
def calculate_fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""

@pytest.fixture
def test_adr() -> dict:
    """Sample ADR for testing."""
    return {
        "title": "Test ADR",
        "context": {
            "problem": "Need to test ADR creation",
            "constraints": ["Must be testable"]
        },
        "options": [
            {
                "title": "Option 1",
                "pros": ["Simple"],
                "cons": ["Basic"]
            }
        ],
        "decision": "Use Option 1 for testing"
    }
