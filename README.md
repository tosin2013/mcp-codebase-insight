# MCP Codebase Insight

MCP Codebase Insight is a server component of the Model Context Protocol (MCP) that provides intelligent analysis and insights into codebases. It uses vector search and machine learning to understand code patterns, architectural decisions, and documentation.

## Features

- 🔍 **Code Analysis**: Analyze code for patterns, best practices, and potential improvements
- 📝 **ADR Management**: Track and manage Architecture Decision Records
- 📚 **Documentation**: Generate and manage technical documentation
- 🧠 **Knowledge Base**: Store and retrieve code patterns and insights using vector search
- 🐛 **Debug System**: Analyze and debug issues with AI assistance
- 📊 **Metrics & Health**: Monitor system health and performance metrics
- 💾 **Caching**: Efficient caching system for improved performance
- 🔒 **Security**: Built-in security features and best practices

## Quick Start

### Using as an MCP Server

1. Create an `mcp.json` file in your project:
```json
{
  "mcpServers": {
    "codebase-insight": {
      "command": "uvicorn",
      "args": [
        "src.mcp_codebase_insight.server:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
      ],
      "env": {
        "PYTHONPATH": "${workspaceRoot}",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8000",
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

2. Install the package in your project:
```bash
pip install mcp-codebase-insight
```

3. Start the server:
```bash
mcp start codebase-insight
```

### Using Docker

```bash
# Pull the image
docker pull modelcontextprotocol/mcp-codebase-insight

# Run the container
docker run -p 3000:3000 \
    --env-file .env \
    -v $(pwd)/docs:/app/docs \
    -v $(pwd)/knowledge:/app/knowledge \
    modelcontextprotocol/mcp-codebase-insight
```

### Local Development Installation

1. Prerequisites:
   - Python 3.11+
   - Rust (for building dependencies)
   - Qdrant vector database

2. Clone the repository:
   ```bash
   git clone https://github.com/modelcontextprotocol/mcp-codebase-insight.git
   cd mcp-codebase-insight
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

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

## Building for Distribution

To use codebase-insight in other directories, you'll need to build and install it:

1. Create a `setup.py`:
```python
from setuptools import setup, find_packages

setup(
    name="mcp-codebase-insight",
    version="0.1.0",
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
pip install path/to/mcp-codebase-insight/dist/mcp_codebase_insight-0.1.0.tar.gz
```

## Configuration

The server can be configured using:
1. Environment variables
2. `.env` file
3. `mcp.json` configuration

Key configuration options:
- `MCP_HOST`: Server host (default: 127.0.0.1)
- `MCP_PORT`: Server port (default: 8000)
- `QDRANT_URL`: Qdrant vector database URL
- `MCP_EMBEDDING_MODEL`: Model for text embeddings
- See [.env.example](.env.example) for more options

## API Documentation

The API documentation is available at `/docs` when the server is running. Key endpoints include:

- `/tools/analyze-code`: Analyze code for patterns
- `/tools/create-adr`: Create Architecture Decision Records
- `/tools/debug-issue`: Debug issues with AI assistance
- `/tools/search-knowledge`: Search the knowledge base
- `/tools/crawl-docs`: Crawl documentation
- `/tools/get-task`: Get task status
- `/health`: Health check endpoint
- `/metrics`: Metrics endpoint

## Development

### Project Structure

```
mcp-codebase-insight/
├── docs/               # Documentation
├── src/               # Source code
│   └── mcp_codebase_insight/
│       ├── core/      # Core functionality
│       └── utils/     # Utilities
├── tests/             # Test suite
├── scripts/           # Utility scripts
└── examples/          # Example code
```

### Development Commands

```bash
# Run tests
pytest tests -v

# Run linters
flake8 src tests

# Format code
black src tests

# Build package
python -m build

# Install locally
pip install -e .
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Model Context Protocol](https://github.com/modelcontextprotocol)
- [Qdrant Vector Database](https://qdrant.tech)
- [sentence-transformers](https://www.sbert.net)
- [FastAPI](https://fastapi.tiangolo.com)

## Support

- 📖 [Documentation](https://github.com/modelcontextprotocol/mcp-codebase-insight/docs)
- 🐛 [Issue Tracker](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
- 💬 [Discussions](https://github.com/modelcontextprotocol/mcp-codebase-insight/discussions)
