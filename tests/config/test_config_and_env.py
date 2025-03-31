"""Tests for configuration and environment handling."""

import sys
import os

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import os
import asyncio
import shutil
import pytest
from pathlib import Path
from typing import Generator
from unittest.mock import patch
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src.mcp_codebase_insight.core.config import ServerConfig
from src.mcp_codebase_insight.server import CodebaseAnalysisServer

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def env_vars(tmp_path):
    """Set up test environment variables and clean up test directories."""
    original_env = dict(os.environ)
    test_dirs = {
        "MCP_DOCS_CACHE_DIR": tmp_path / "test_docs",
        "MCP_ADR_DIR": tmp_path / "test_docs/adrs",
        "MCP_KB_STORAGE_DIR": tmp_path / "test_knowledge",
        "MCP_DISK_CACHE_DIR": tmp_path / "test_cache"
    }
    
    test_vars = {
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8000",
        "MCP_LOG_LEVEL": "DEBUG",
        "MCP_DEBUG": "true",
        "MCP_METRICS_ENABLED": "true",
        "MCP_CACHE_ENABLED": "true",
        "MCP_QDRANT_URL": "http://localhost:6333"  # Use local Qdrant server
    }
    test_vars.update({k: str(v) for k, v in test_dirs.items()})
    
    os.environ.update(test_vars)
    yield test_vars
    
    # Clean up test directories
    for dir_path in test_dirs.values():
        if dir_path.exists():
            shutil.rmtree(dir_path, ignore_errors=True)
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def test_collection_name() -> str:
    """Generate a unique test collection name."""
    return f"test_collection_{uuid.uuid4().hex[:8]}"

@pytest.fixture
async def qdrant_client() -> QdrantClient:
    """Create a Qdrant client for tests."""
    client = QdrantClient(url="http://localhost:6333")
    yield client
    client.close()

@pytest.mark.asyncio
async def test_server_config_from_env(env_vars, tmp_path, test_collection_name: str, qdrant_client: QdrantClient):
    """Test server configuration from environment variables."""
    config = ServerConfig(
        host=env_vars["MCP_HOST"],
        port=int(env_vars["MCP_PORT"]),
        log_level=env_vars["MCP_LOG_LEVEL"],
        debug_mode=env_vars["MCP_DEBUG"].lower() == "true",
        docs_cache_dir=Path(env_vars["MCP_DOCS_CACHE_DIR"]),
        adr_dir=Path(env_vars["MCP_ADR_DIR"]),
        kb_storage_dir=Path(env_vars["MCP_KB_STORAGE_DIR"]),
        disk_cache_dir=Path(env_vars["MCP_DISK_CACHE_DIR"]),
        qdrant_url=env_vars["MCP_QDRANT_URL"],
        collection_name=test_collection_name
    )
    
    # Create test collection
    try:
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)
        
        qdrant_client.create_collection(
            collection_name=test_collection_name,
            vectors_config=VectorParams(
                size=384,  # Default size for all-MiniLM-L6-v2
                distance=Distance.COSINE
            )
        )
        
        server = CodebaseAnalysisServer(config)
        await server.initialize()
        
        assert server.config.host == env_vars["MCP_HOST"]
        assert server.config.port == int(env_vars["MCP_PORT"])
        assert server.config.log_level == env_vars["MCP_LOG_LEVEL"]
        assert server.config.debug_mode == (env_vars["MCP_DEBUG"].lower() == "true")
        assert isinstance(server.config.docs_cache_dir, Path)
        assert isinstance(server.config.adr_dir, Path)
        assert isinstance(server.config.kb_storage_dir, Path)
        assert isinstance(server.config.disk_cache_dir, Path)
    finally:
        await server.shutdown()
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)

@pytest.mark.asyncio
async def test_directory_creation(tmp_path, test_collection_name: str, qdrant_client: QdrantClient):
    """Test directory creation."""
    config = ServerConfig(
        host="localhost",
        port=8000,
        docs_cache_dir=tmp_path / "docs",
        adr_dir=tmp_path / "docs/adrs",
        kb_storage_dir=tmp_path / "knowledge",
        disk_cache_dir=tmp_path / "cache",
        qdrant_url="http://localhost:6333",
        collection_name=test_collection_name,
        cache_enabled=True  # Explicitly enable cache for clarity
    )
    
    # Create test collection
    try:
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)
        
        qdrant_client.create_collection(
            collection_name=test_collection_name,
            vectors_config=VectorParams(
                size=384,  # Default size for all-MiniLM-L6-v2
                distance=Distance.COSINE
            )
        )
        
        # Create and initialize server
        server = CodebaseAnalysisServer(config)
        await server.initialize()
        
        # Verify directories were created
        assert (tmp_path / "docs").exists(), "Docs directory was not created"
        assert (tmp_path / "docs/adrs").exists(), "ADR directory was not created"
        assert (tmp_path / "knowledge").exists(), "Knowledge directory was not created"
        assert (tmp_path / "cache").exists(), "Cache directory was not created"
    finally:
        await server.shutdown()
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)

@pytest.mark.asyncio
async def test_directory_creation_with_none_cache_dir(tmp_path, test_collection_name: str, qdrant_client: QdrantClient):
    """Test server startup with None disk_cache_dir."""
    config = ServerConfig(
        host="localhost",
        port=8000,
        docs_cache_dir=tmp_path / "docs",
        adr_dir=tmp_path / "docs/adrs",
        kb_storage_dir=tmp_path / "knowledge",
        disk_cache_dir=None,  # Explicitly set to None
        qdrant_url="http://localhost:6333",
        collection_name=test_collection_name,
        cache_enabled=True  # But keep cache enabled
    )
    
    # Create test collection
    try:
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)
        
        qdrant_client.create_collection(
            collection_name=test_collection_name,
            vectors_config=VectorParams(
                size=384,  # Default size for all-MiniLM-L6-v2
                distance=Distance.COSINE
            )
        )
        
        # Initialize server
        server = CodebaseAnalysisServer(config)
        await server.initialize()
        
        # When disk_cache_dir is None but cache is enabled, we should default to Path("cache")
        assert config.disk_cache_dir == Path("cache"), "disk_cache_dir should default to 'cache'"
        assert Path("cache").exists(), "Default cache directory should exist"
    finally:
        await server.shutdown()
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)

@pytest.mark.asyncio
async def test_directory_creation_with_cache_disabled(tmp_path, test_collection_name: str, qdrant_client: QdrantClient):
    """Test server startup with caching disabled."""
    config = ServerConfig(
        host="localhost",
        port=8000,
        docs_cache_dir=tmp_path / "docs",
        adr_dir=tmp_path / "docs/adrs",
        kb_storage_dir=tmp_path / "knowledge",
        disk_cache_dir=Path(tmp_path / "cache"),  # Set a path
        qdrant_url="http://localhost:6333",
        collection_name=test_collection_name,
        cache_enabled=False  # But disable caching
    )
    
    # Create test collection
    try:
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)
        
        qdrant_client.create_collection(
            collection_name=test_collection_name,
            vectors_config=VectorParams(
                size=384,  # Default size for all-MiniLM-L6-v2
                distance=Distance.COSINE
            )
        )
        
        # Server initialization should set disk_cache_dir to None when cache_enabled is False
        server = CodebaseAnalysisServer(config)
        await server.initialize()
        
        # Verify that disk_cache_dir is None when cache_enabled is False
        assert config.disk_cache_dir is None, "disk_cache_dir should be None when cache_enabled is False"
        # And that the cache directory does not exist
        assert not (tmp_path / "cache").exists(), "Cache directory should not exist when cache is disabled"
    finally:
        await server.shutdown()
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)

@pytest.mark.asyncio
async def test_directory_creation_permission_error(tmp_path, test_collection_name: str, qdrant_client: QdrantClient):
    """Test directory creation with permission error."""
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o444)  # Read-only
    
    config = ServerConfig(
        host="localhost",
        port=8000,
        docs_cache_dir=readonly_dir / "docs",
        adr_dir=readonly_dir / "docs/adrs",
        kb_storage_dir=readonly_dir / "knowledge",
        disk_cache_dir=readonly_dir / "cache",
        qdrant_url="http://localhost:6333",
        collection_name=test_collection_name
    )
    
    server = None
    try:
        # Create test collection
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)
        
        qdrant_client.create_collection(
            collection_name=test_collection_name,
            vectors_config=VectorParams(
                size=384,  # Default size for all-MiniLM-L6-v2
                distance=Distance.COSINE
            )
        )
        
        server = CodebaseAnalysisServer(config)
        with pytest.raises(RuntimeError) as exc_info:
            await server.initialize()
        assert "Permission denied" in str(exc_info.value)
    finally:
        if server:
            await server.shutdown()
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)
        # Clean up the readonly directory
        readonly_dir.chmod(0o777)  # Restore write permissions for cleanup
        if readonly_dir.exists():
            shutil.rmtree(readonly_dir)

@pytest.mark.asyncio
async def test_directory_already_exists(tmp_path, test_collection_name: str, qdrant_client: QdrantClient):
    """Test server initialization with pre-existing directories."""
    # Create directories before server initialization
    dirs = [
        tmp_path / "docs",
        tmp_path / "docs/adrs",
        tmp_path / "knowledge",
        tmp_path / "cache"
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    config = ServerConfig(
        host="localhost",
        port=8000,
        docs_cache_dir=tmp_path / "docs",
        adr_dir=tmp_path / "docs/adrs",
        kb_storage_dir=tmp_path / "knowledge",
        disk_cache_dir=tmp_path / "cache",
        qdrant_url="http://localhost:6333",
        collection_name=test_collection_name
    )
    
    # Create test collection
    try:
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)
        
        qdrant_client.create_collection(
            collection_name=test_collection_name,
            vectors_config=VectorParams(
                size=384,  # Default size for all-MiniLM-L6-v2
                distance=Distance.COSINE
            )
        )
        
        server = CodebaseAnalysisServer(config)
        await server.initialize()
        
        # Verify directories still exist and are accessible
        for dir_path in dirs:
            assert dir_path.exists()
            assert os.access(dir_path, os.R_OK | os.W_OK)
    finally:
        await server.shutdown()
        if test_collection_name in [c.name for c in qdrant_client.get_collections().collections]:
            qdrant_client.delete_collection(test_collection_name)
        # Clean up
        for dir_path in dirs:
            if dir_path.exists():
                shutil.rmtree(dir_path) 