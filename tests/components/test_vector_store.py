import pytest
import uuid
import sys
import os
from pathlib import Path
from typing import AsyncGenerator, Dict
from fastapi.testclient import TestClient
# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.mcp_codebase_insight.core.vector_store import VectorStore
from src.mcp_codebase_insight.core.config import ServerConfig
from src.mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
async def test_metadata() -> Dict:
    """Standard test metadata for consistency across tests."""
    return {
        "type": "code",
        "language": "python",
        "title": "Test Code",
        "description": "Test code snippet for vector store testing",
        "tags": ["test", "vector"]
    }

@pytest.fixture
async def embedder():
    return SentenceTransformerEmbedding()

@pytest.fixture
async def vector_store(test_config: ServerConfig, embedder):
    store = VectorStore(test_config.qdrant_url, embedder)
    await store.initialize()
    yield store
    await store.cleanup()

@pytest.mark.asyncio
async def test_vector_store_initialization(vector_store: VectorStore):
    """Test that vector store initializes correctly."""
    assert vector_store is not None
    assert vector_store.embedder is not None
    assert vector_store.client is not None
    assert vector_store.initialized is True
    logger.info("Vector store initialization test passed")

@pytest.mark.asyncio
async def test_vector_store_add_and_search(vector_store: VectorStore, test_metadata: Dict):
    """Test adding and searching vectors."""
    # Test data
    test_text = "Test code snippet with unique identifier"
    
    # Add vector
    logger.info("Adding vector to store")
    vector_id = await vector_store.add_vector(test_text, test_metadata)
    assert vector_id is not None
    
    # Search for similar vectors
    logger.info("Searching for similar vectors")
    results = await vector_store.search_similar(test_text, limit=1)
    assert len(results) > 0
    
    # Use get() with default value for safety
    assert results[0].metadata.get("type", "unknown") == "code"
    
    # Log metadata for debugging
    logger.info(f"Original metadata: {test_metadata}")
    logger.info(f"Retrieved metadata: {results[0].metadata}")
    
    # Verify all expected metadata fields are present
    missing_keys = []
    for key in test_metadata:
        if key not in results[0].metadata:
            missing_keys.append(key)
    
    assert not missing_keys, f"Metadata is missing expected keys: {missing_keys}"
    
    logger.info("Vector store add and search test passed")

@pytest.mark.asyncio
async def test_vector_store_cleanup(test_config: ServerConfig, embedder: SentenceTransformerEmbedding):
    """Test that cleanup works correctly."""
    # Use the configured collection name for this test
    # This ensures we're using the properly initialized collection
    collection_name = os.environ.get("MCP_COLLECTION_NAME", test_config.collection_name)
    
    store = VectorStore(
        test_config.qdrant_url,
        embedder,
        collection_name=collection_name
    )
    
    logger.info(f"Initializing vector store with collection {collection_name}")
    await store.initialize()
    assert store.initialized is True
    
    # Add a vector to verify there's something to clean up
    await store.add_vector("Test cleanup text", {"type": "test"})
    
    # Now clean up
    logger.info(f"Cleaning up vector store with collection {collection_name}")
    await store.cleanup()
    
    # Verify the store is no longer initialized
    assert store.initialized is False
    
    # Clean up remaining resources
    await store.close()
    
    logger.info("Vector store cleanup test passed") 