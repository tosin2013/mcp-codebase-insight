import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from .core.config import ServerConfig
from .server import CodebaseAnalysisServer

def main():
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
        kb_storage_dir=Path(os.getenv("KB_STORAGE_DIR", "knowledge"))
    )

    # Create and start server
    server = CodebaseAnalysisServer(config)
    server.start(
        host=config.host,
        port=config.port
    )

if __name__ == "__main__":
    main()
