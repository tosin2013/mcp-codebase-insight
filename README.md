# MCP Codebase Insight

[![CI/CD](https://github.com/tosin2013/mcp-codebase-insight/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/tosin2013/mcp-codebase-insight/actions/workflows/ci-cd.yml)
[![PyPI version](https://badge.fury.io/py/mcp-codebase-insight.svg)](https://badge.fury.io/py/mcp-codebase-insight)
[![Python Versions](https://img.shields.io/pypi/pyversions/mcp-codebase-insight.svg)](https://pypi.org/project/mcp-codebase-insight/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/tosin2013/mcp-codebase-insight/branch/main/graph/badge.svg)](https://codecov.io/gh/tosin2013/mcp-codebase-insight)

A Model Context Protocol (MCP) server that provides advanced codebase analysis capabilities to LLMs like Claude. The server integrates with Qdrant vector database to provide semantic search and pattern matching across codebases.

## Features

- **Code Analysis**: Analyze code patterns, architecture, and potential improvements
- **ADR Management**: Create and manage Architectural Decision Records (ADRs)
- **Systematic Debugging**: Debug issues using Agans' 9 Rules methodology
- **Documentation Management**: Crawl, store, and search technical documentation
- **Knowledge Base**: Store and retrieve development patterns and solutions
- **Vector Search**: Semantic search across code and documentation
- **Metrics & Health**: Monitor system performance and health

## Installation

### PyPI Installation (Recommended)

```bash
# Install the package
pip install mcp-codebase-insight

# Start Qdrant container
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest

# Start the server
mcp-codebase-insight
```

### Development Installation

1. Clone the repository:
```bash
git clone https://github.com/tosin2013/mcp-codebase-insight.git
cd mcp-codebase-insight
```

2. Install dependencies:
```bash
make install-dev
```

3. Start Qdrant container:
```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:consistent \
  qdrant/qdrant:latest
```

4. Start the server:
```bash
make start
```

The server will be available at http://localhost:3000.

## Development Setup

1. Install development dependencies:
```bash
make install-dev
```

2. Load example patterns:
```bash
make load-patterns
```

3. Run tests:
```bash
make test
```

4. Run example:
```bash
make example
```

## Usage with Claude

Here's a simple example of using the server with Claude:

```python
import asyncio
from examples.use_with_claude import analyze_code

async def main():
    # Analyze code
    result = await analyze_code(
        code="""
        def process_data(data):
            results = []
            for item in data:
                if item.get('active'):
                    value = item.get('value', 0)
                    if value > 100:
                        results.append(value * 2)
            return results
        """,
        context={
            "language": "python",
            "purpose": "data processing"
        }
    )
    print(result)

asyncio.run(main())
```

See `examples/use_with_claude.py` for more examples.

## Claude Desktop Integration

To use this MCP server with Claude Desktop:

1. Open Claude Desktop's configuration file:
```bash
# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. Add the MCP server configuration to the `mcpServers` object:
```json
{
  "mcpServers": {
    "codebase-insight": {
      "command": "mcp-codebase-insight",
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "codebase_analysis",
        "LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

3. Restart Claude Desktop for the changes to take effect.

The MCP server will now be available to Claude through the desktop app, providing access to all codebase analysis tools.

## Available Tools

The server provides the following MCP tools:

- `analyze-code`: Analyze code patterns and architecture
  - Required: `code` (non-empty string)
  - Optional: `context` (object)

- `create-adr`: Create architectural decision records
  - Required: `title` (non-empty string), `decision` (non-empty string)
  - Optional: `context` (object), `options` (array)

- `debug-issue`: Debug issues systematically
  - Required: `description` (non-empty string)
  - Optional: `type` (string), `context` (object)

- `crawl-docs`: Crawl and store documentation
  - Required: `urls` (non-empty array), `source_type` (non-empty string)

- `search-knowledge`: Search knowledge base
  - Required: `query` (non-empty string)
  - Optional: `type` (string), `limit` (number, default: 5)

- `get-task`: Get task status and results
  - Required: `task_id` (non-empty string)

## Response Format

All tools return responses in a standardized format:

```json
{
  "content": [
    {
      // Tool-specific response data
    }
  ],
  "isError": false
}
```

Error responses follow the same format with `isError: true`:

```json
{
  "content": [
    {
      "error": "Error message",
      "step": "step_id"  // Optional, included for task failures
    }
  ],
  "isError": true
}
```

## Configuration

Configuration is handled through environment variables or `.env` file:

```env
# Server settings
HOST=127.0.0.1
PORT=3000
LOG_LEVEL=INFO

# Qdrant settings (Docker)
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=codebase_analysis

# Cache settings
CACHE_ENABLED=true
CACHE_SIZE=1000
CACHE_TTL=3600

# Documentation settings
DOCS_CACHE_DIR=references
DOCS_REFRESH_INTERVAL=86400
DOCS_MAX_SIZE=1000000

# Knowledge base settings
KB_STORAGE_DIR=knowledge
KB_BACKUP_INTERVAL=86400
KB_MAX_PATTERNS=10000
```

## Project Structure

```
mcp-server-qdrant/
├── src/
│   └── mcp_server_qdrant/
│       ├── core/           # Core components
│       ├── utils/          # Utilities
│       ├── server.py       # MCP server implementation
│       └── main.py         # Entry point
├── tests/                  # Test suite
├── docs/                   # Documentation
│   ├── adrs/              # Architectural Decision Records
│   └── templates/         # Templates
├── scripts/               # Utility scripts
├── examples/              # Usage examples
└── knowledge/            # Knowledge base storage
```

## Development Commands

The project includes a Makefile with common commands:

```bash
make help              # Show available commands
make install          # Install dependencies
make install-dev      # Install development dependencies
make start           # Start server
make stop            # Stop server
make test            # Run tests
make lint            # Run linters
make format          # Format code
make check           # Run all checks
make load-patterns   # Load example patterns
make example         # Run example script
make adr             # Create new ADR
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting: `make check`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Model Context Protocol](https://github.com/anthropics/anthropic-tools) for the MCP specification
- [Qdrant](https://qdrant.tech/) for vector similarity search
- [sentence-transformers](https://www.sbert.net/) for text embeddings
