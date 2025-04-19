#!/usr/bin/env python3
"""
Vector Store Validation Script
Tests vector store operations using local codebase.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from mcp_codebase_insight.core.vector_store import VectorStore
from mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def validate_vector_store(config: dict) -> bool:
    """Validate vector store operations."""
    logger.info("Testing vector store operations...")
    
    try:
        # Initialize embedder
        embedder = SentenceTransformerEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        await embedder.initialize()
        logger.info("Embedder initialized successfully")
        
        # Initialize vector store
        vector_store = VectorStore(
            url=config.get("QDRANT_URL", "http://localhost:6333"),
            embedder=embedder,
            collection_name=config.get("COLLECTION_NAME", "mcp-codebase-insight"),
            api_key=config.get("QDRANT_API_KEY", ""),
            vector_name="default"
        )
        await vector_store.initialize()
        logger.info("Vector store initialized successfully")
        
        # Test vector operations
        test_text = "def test_function():\n    pass"
        embedding = await embedder.embed(test_text)
        
        # Store vector
        await vector_store.add_vector(
            text=test_text,
            metadata={"type": "code", "content": test_text}
        )
        logger.info("Vector storage test passed")
        
        # Search for similar vectors
        logger.info("Searching for similar vectors")
        results = await vector_store.search_similar(
            query=test_text,
            limit=1
        )
        
        if not results or len(results) == 0:
            logger.error("Vector search test failed: No results found")
            return False
            
        logger.info("Vector search test passed")
        
        # Verify result metadata
        result = results[0]
        if not result.metadata or result.metadata.get("type") != "code":
            logger.error("Vector metadata test failed: Invalid metadata")
            return False
            
        logger.info("Vector metadata test passed")
        return True
        
    except Exception as e:
        logger.error(f"Vector store validation failed: {e}")
        return False

if __name__ == "__main__":
    # Load config from environment or .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    import os
    config = {
        "QDRANT_URL": os.getenv("QDRANT_URL", "http://localhost:6333"),
        "COLLECTION_NAME": os.getenv("COLLECTION_NAME", "mcp-codebase-insight"),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY", "")
    }
    
    success = asyncio.run(validate_vector_store(config))
    sys.exit(0 if success else 1) 