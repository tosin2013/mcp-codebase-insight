"""Command-line interface for MCP Codebase Insight."""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.server import CodebaseAnalysisServer

def main():
    """Start the MCP server."""
    # Load environment variables
    load_dotenv()

    # Create server config
    config = ServerConfig(
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "3000")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        docs_cache_dir=Path(os.getenv("DOCS_CACHE_DIR", "references")),
        adr_dir=Path(os.getenv("ADR_DIR", "docs/adrs")),
        adr_template_path=Path(os.getenv("ADR_TEMPLATE_PATH", "docs/templates/adr.md")),
        kb_storage_dir=Path(os.getenv("KB_STORAGE_DIR", "knowledge")),
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        collection_name=os.getenv("COLLECTION_NAME", "codebase_analysis")
    )

    # Create and start server
    server = CodebaseAnalysisServer(config)
    server.start(
        host=config.host,
        port=config.port
    )

if __name__ == "__main__":
    main()
