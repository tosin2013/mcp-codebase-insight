# Configuration Guide

This guide covers the various configuration options for MCP Codebase Insight, including environment variables, command line arguments, and configuration files.

## Environment Variables

The MCP Codebase Insight server can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| MCP_HOST | Host address to bind the server to | 127.0.0.1 |
| MCP_PORT | Port to run the server on | 3000 |
| MCP_LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| MCP_DEBUG | Enable debug mode | false |
| QDRANT_URL | URL of the Qdrant vector database | http://localhost:6333 |
| QDRANT_API_KEY | API key for the Qdrant vector database | (no default) |
| MCP_EMBEDDING_MODEL | Name of the embedding model to use | all-MiniLM-L6-v2 |
| MCP_COLLECTION_NAME | Name of the collection in Qdrant | codebase_patterns |
| MCP_DOCS_CACHE_DIR | Directory for document cache | docs |
| MCP_ADR_DIR | Directory for Architecture Decision Records | docs/adrs |
| MCP_KB_STORAGE_DIR | Directory for knowledge base storage | knowledge |
| MCP_DISK_CACHE_DIR | Directory for disk cache | cache |
| MCP_METRICS_ENABLED | Enable metrics collection | true |
| MCP_CACHE_ENABLED | Enable caching | true |
| MCP_MEMORY_CACHE_SIZE | Size of the memory cache | 1000 |

### Setting Environment Variables

#### Unix/Linux/MacOS

```bash
# Set environment variables for the current session
export MCP_HOST=127.0.0.1
export MCP_PORT=3000
export QDRANT_URL=http://localhost:6333

# Or set them all at once with a .env file
set -a
source .env
set +a
```

#### Windows Command Prompt

```cmd
set MCP_HOST=127.0.0.1
set MCP_PORT=3000
set QDRANT_URL=http://localhost:6333
```

#### Windows PowerShell

```powershell
$env:MCP_HOST = "127.0.0.1"
$env:MCP_PORT = "3000"
$env:QDRANT_URL = "http://localhost:6333"
```

### Using .env Files

You can also create a `.env` file in your project root to automatically set these variables:

```
MCP_HOST=127.0.0.1
MCP_PORT=3000
MCP_LOG_LEVEL=INFO
QDRANT_URL=http://localhost:6333
MCP_DOCS_CACHE_DIR=./docs
MCP_ADR_DIR=./docs/adrs
MCP_KB_STORAGE_DIR=./knowledge
MCP_DISK_CACHE_DIR=./cache
```

Then load the environment variables:

```bash
# Using python-dotenv in your code
from dotenv import load_dotenv
load_dotenv()

# Or before running the server
source .env  # Unix/Linux/MacOS
```

## Command Line Arguments

You can also configure some of these settings through command line arguments when starting the server:

```bash
mcp-codebase-insight --host 127.0.0.1 --port 3000 --log-level INFO --debug
```

Command line arguments take precedence over environment variables.

Available command line options:
- `--host`: Host address to bind the server to (default: 127.0.0.1)
- `--port`: Port to run the server on (default: 3000)
- `--log-level`: Set the logging level (choices: DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--debug`: Enable debug mode

## Configuration Files

### mcp.json

The `mcp.json` file is used to configure how the MCP server runs in your development environment:

```json
{
  "mcpServers": {
    "codebase-insight": {
      "command": "mcp-codebase-insight",
      "args": [
        "--host",
        "127.0.0.1",
        "--port",
        "3000",
        "--log-level",
        "INFO"
      ],
      "env": {
        "PYTHONPATH": "${workspaceRoot}",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "3000",
        "MCP_LOG_LEVEL": "INFO",
        "QDRANT_URL": "http://localhost:6333",
        "MCP_DOCS_CACHE_DIR": "${workspaceRoot}/docs",
        "MCP_ADR_DIR": "${workspaceRoot}/docs/adrs",
        "MCP_KB_STORAGE_DIR": "${workspaceRoot}/knowledge",
        "MCP_DISK_CACHE_DIR": "${workspaceRoot}/cache"
      }
    }
  }
}
```

### Docker Environment Configuration

For Docker deployments, you should create a `.env` file with the appropriate settings:

```
MCP_HOST=0.0.0.0
MCP_PORT=3000
MCP_LOG_LEVEL=INFO
QDRANT_URL=http://host.docker.internal:6333
MCP_DOCS_CACHE_DIR=/app/docs
MCP_ADR_DIR=/app/docs/adrs
MCP_KB_STORAGE_DIR=/app/knowledge
MCP_DISK_CACHE_DIR=/app/cache
```

> **Note:** When using Docker, the host is set to `0.0.0.0` to allow connections from outside the container. If your Qdrant instance is running on the host machine, use `host.docker.internal` instead of `localhost`.

## Production Considerations

For production deployments, consider these additional configuration best practices:

1. **Security**:
   - Use HTTPS with proper certificates
   - Set a strong API key
   - Restrict network access to the server
   - Use an isolated Qdrant instance

2. **Performance**:
   - Increase cache size for larger codebases
   - Use a dedicated server with sufficient RAM
   - Consider using a distributed setup for large teams

3. **Reliability**:
   - Set up proper logging
   - Configure health checks
   - Use a process manager like systemd, supervisor, or PM2
