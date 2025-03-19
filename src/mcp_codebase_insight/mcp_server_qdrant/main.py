import asyncio
import signal
import sys
from pathlib import Path
import click
from typing import Optional

from .core.config import ServerConfig
from .server import CodebaseAnalysisServer
from .utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

async def run_server(
    host: str,
    port: int,
    qdrant_url: str,
    collection_name: str,
    log_level: str,
    docs_dir: Optional[Path] = None,
    kb_dir: Optional[Path] = None
):
    """Run the MCP server."""
    # Setup logging
    setup_logging(log_level)
    
    # Create configuration
    config = ServerConfig(
        qdrant_url=qdrant_url,
        collection_name=collection_name,
        host=host,
        port=port,
        log_level=log_level
    )
    
    if docs_dir:
        config.docs_cache_dir = docs_dir
    if kb_dir:
        config.kb_storage_dir = kb_dir
    
    # Create and start server
    server = CodebaseAnalysisServer(config)
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    
    async def shutdown(signal=None):
        """Cleanup and shutdown."""
        if signal:
            logger.info(f"Received exit signal {signal.name}...")
        
        logger.info("Shutting down server...")
        await server.stop()
        
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        
        logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        loop.stop()
        logger.info("Shutdown complete.")
    
    # Handle signals
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s))
        )
    
    try:
        # Start server
        await server.start()
        logger.info(f"Server running at {host}:{port}")
        
        # Keep running until stopped
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        logger.info("Server task cancelled")
        await shutdown()
    except Exception as e:
        logger.error(f"Server error: {e}")
        await shutdown()
        sys.exit(1)

@click.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind server to"
)
@click.option(
    "--port",
    default=3000,
    type=int,
    help="Port to bind server to"
)
@click.option(
    "--qdrant-url",
    default="http://localhost:6333",
    help="URL of Qdrant server"
)
@click.option(
    "--collection",
    default="codebase_analysis",
    help="Name of Qdrant collection"
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Logging level"
)
@click.option(
    "--docs-dir",
    type=click.Path(path_type=Path),
    help="Directory for documentation cache"
)
@click.option(
    "--kb-dir",
    type=click.Path(path_type=Path),
    help="Directory for knowledge base storage"
)
def main(
    host: str,
    port: int,
    qdrant_url: str,
    collection: str,
    log_level: str,
    docs_dir: Optional[Path],
    kb_dir: Optional[Path]
):
    """Run the Codebase Analysis MCP Server."""
    try:
        asyncio.run(
            run_server(
                host=host,
                port=port,
                qdrant_url=qdrant_url,
                collection_name=collection,
                log_level=log_level,
                docs_dir=docs_dir,
                kb_dir=kb_dir
            )
        )
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
