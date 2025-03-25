# Installation Guide

This guide covers different methods to install and set up MCP Codebase Insight.

## Using as an MCP Server

1. Create an `mcp.json` file in your project:
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

> **Note:** `${workspaceRoot}` is a placeholder that refers to your project's root directory. If configuring manually, replace it with the absolute path to your project directory.

2. Install the package in your project:
```bash
pip install mcp-codebase-insight
```

3. Start the server:
```bash
mcp-codebase-insight --host 127.0.0.1 --port 3000 --log-level INFO
```

> **Note:** Ensure the port in your startup command (3000 in this example) matches the port specified in your mcp.json configuration.

## Qdrant Setup

> **Important**: MCP Codebase Insight requires a running Qdrant vector database instance. Without Qdrant, the system cannot store or search vector embeddings.

### Option 1: Using Docker (Recommended)

The easiest way to set up Qdrant is using Docker:

```bash
# Pull and run Qdrant container
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_data:/qdrant/storage \
    qdrant/qdrant
```

This will start Qdrant on port 6333 (API) and 6334 (web UI).

### Option 2: Using Docker Compose

You can set up both MCP Codebase Insight and Qdrant using Docker Compose. See the [Docker Setup](./docker-setup.md#using-docker-compose) guide for details.

### Option 3: Manual Installation

For manual installation, follow the official Qdrant documentation:
[Qdrant Installation Guide](https://qdrant.tech/documentation/guides/installation/)

### Verifying Qdrant Installation

To verify that Qdrant is running properly:

```bash
# Check Qdrant health
curl http://localhost:6333/health
```

You should receive a response indicating the service is healthy.

## Local Development Installation

1. Prerequisites:
   - Python 3.11+ (3.12 recommended)
   - Rust 1.70+ (for building dependencies)
   - Qdrant vector database

2. Clone the repository:
   ```bash
   git clone https://github.com/tosin2013/mcp-codebase-insight.git
   cd mcp-codebase-insight
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

   > **Best Practice:** Always create the virtual environment in your project directory and activate it in each new terminal session before working on the project.

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. Run the server:
   ```bash
   uvicorn src.mcp_codebase_insight.server:app --reload
   ```

   > **Warning:** The `--reload` flag is for development only. Do not use it in production environments as it may cause performance issues and unexpected behavior.

## Building for Distribution

To use codebase-insight in other directories, you'll need to build and install it:

1. Create a `setup.py`:
```python
from setuptools import setup, find_packages

setup(
    name="mcp-codebase-insight",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.103.2",
        "uvicorn>=0.23.2",
        "pydantic>=2.4.2",
        "qdrant-client>=1.13.3",
        "sentence-transformers>=2.2.2",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.11",
)
```

2. Build the package:
```bash
pip install build
python -m build
```

3. Install in another project:
```bash
pip install path/to/mcp-codebase-insight/dist/mcp_codebase_insight-0.2.0.tar.gz
```
