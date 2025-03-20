"""ASGI application entry point."""

from .core.config import ServerConfig
from .server import CodebaseAnalysisServer

# Create server instance with default config
config = ServerConfig()
server = CodebaseAnalysisServer(config)

# Export the FastAPI app instance
app = server.app 