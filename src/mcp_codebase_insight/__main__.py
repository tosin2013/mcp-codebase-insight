"""Main entry point for MCP server."""

import asyncio
import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from .core.config import ServerConfig
from .core.embeddings import SentenceTransformerEmbedding
from .core.vector_store import VectorStore
from .server import CodebaseAnalysisServer
from .utils.logger import get_logger

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger(__name__)

def get_config() -> ServerConfig:
    """Get server configuration."""
    return ServerConfig(
        host=os.getenv("MCP_HOST", "127.0.0.1"),
        port=int(os.getenv("MCP_PORT", "3000")),
        log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        docs_cache_dir=Path(os.getenv("MCP_DOCS_CACHE_DIR", "docs")),
        adr_dir=Path(os.getenv("MCP_ADR_DIR", "docs/adrs")),
        kb_storage_dir=Path(os.getenv("MCP_KB_STORAGE_DIR", "knowledge")),
        embedding_model=os.getenv("MCP_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        collection_name=os.getenv("MCP_COLLECTION_NAME", "codebase_patterns"),
        debug_mode=os.getenv("MCP_DEBUG", "false").lower() == "true",
        metrics_enabled=os.getenv("MCP_METRICS_ENABLED", "true").lower() == "true",
        cache_enabled=os.getenv("MCP_CACHE_ENABLED", "true").lower() == "true",
        memory_cache_size=int(os.getenv("MCP_MEMORY_CACHE_SIZE", "1000")),
        disk_cache_dir=Path(os.getenv("MCP_DISK_CACHE_DIR", "cache")) if os.getenv("MCP_DISK_CACHE_DIR") else None
    )

async def main():
    """Main entry point."""
    try:
        # Get configuration
        config = get_config()
        
        # Initialize components
        embedder = SentenceTransformerEmbedding(config.embedding_model)
        vector_store = VectorStore(
            url=config.qdrant_url,
            embedder=embedder,
            collection_name=config.collection_name
        )
        
        # Create server
        server = CodebaseAnalysisServer(config)
        
        # Initialize server
        await server.start()
        
        # Run server
        config_dict = {
            "app": server.app,
            "host": config.host,
            "port": config.port,
            "log_level": config.log_level.lower(),
            "reload": config.debug_mode
        }
        
        if config.debug_mode:
            logger.info(
                "Starting server in debug mode",
                host=config.host,
                port=config.port
            )
        else:
            logger.info(
                "Starting server",
                host=config.host,
                port=config.port
            )
            
        uvicorn.run(**config_dict)
        
    except Exception as e:
        logger.exception("Error starting server", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(main())
