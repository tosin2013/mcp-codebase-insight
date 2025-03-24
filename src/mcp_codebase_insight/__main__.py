"""Main entry point for MCP server."""

import os
from pathlib import Path
import sys
import logging

import uvicorn
from dotenv import load_dotenv

from .core.config import ServerConfig
from .server import create_app
from .utils.logger import get_logger

# Configure logging
logger = get_logger(__name__)

def get_config() -> ServerConfig:
    """Get server configuration."""
    try:
        # Load environment variables
        load_dotenv()
        
        config = ServerConfig(
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
        
        logger.info("Configuration loaded successfully")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        raise

def main():
    """Run the server."""
    try:
        # Get configuration
        config = get_config()
        
        # Create FastAPI app
        app = create_app(config)
        
        # Log startup message
        logger.info(
            f"Starting MCP Codebase Insight Server on {config.host}:{config.port} "
            f"(log level: {config.log_level}, debug mode: {config.debug_mode})"
        )
        
        # Run using Uvicorn directly
        uvicorn.run(
            app=app,
            host=config.host,
            port=config.port,
            log_level=config.log_level.lower(),
            loop="auto",
            lifespan="on",
            workers=1
        )
        
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Run main directly without asyncio.run()
    main()
