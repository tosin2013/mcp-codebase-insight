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
- 🔄 **Build Verification**: Automated end-to-end build verification with contextual analysis

## Quick Start

### Using as an MCP Server

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

2. Install the package in your project:
```bash
pip install mcp-codebase-insight
```

3. Start the server:
```bash
mcp-codebase-insight --host 127.0.0.1 --port 8000 --log-level INFO
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
    tosin2013/mcp-codebase-insight
```

### Local Development Installation

1. Prerequisites:
   - Python 3.11+
   - Rust (for building dependencies)
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

## Configuration

### Environment Variables

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

You can set these variables in a `.env` file in the project root directory, or through your system's environment variables.

### Using Command Line Arguments

You can also configure some of these settings through command line arguments when starting the server:

```bash
python -m src.mcp_codebase_insight.server --host 127.0.0.1 --port 3000 --log-level INFO --debug
```

Command line arguments take precedence over environment variables.

### Setting up mcp.json

The `mcp.json` file is used to configure how the MCP server runs in your development environment. Create this file in your project's root directory:

1. Create a new file named `mcp.json` in your project root
2. Add the following configuration, adjusting paths and settings as needed:

```json
{
  "mcpServers": {
    "codebase-insight": {
      "command": "mcp-codebase-insight",
      "args": [
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--log-level",
        "INFO"
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

This configuration:
- Sets up the server to run on localhost:8000
- Configures logging and debugging options
- Specifies paths for documentation, ADRs, and caching
- Sets the Qdrant vector database URL

You can customize these settings based on your needs. The server supports the following command-line options:
- `--host`: Host address to bind the server to (default: 127.0.0.1)
- `--port`: Port to run the server on (default: 3000)
- `--log-level`: Set the logging level (choices: DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--debug`: Enable debug mode

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

## Build Verification

The system includes an automated end-to-end build verification process that ensures all components are correctly integrated and the system functions as intended.

### How Build Verification Works

1. **Relationship Analysis**: First, the system analyzes the codebase to extract relationships between components and stores them in the vector database.

2. **Build Verification**: Next, it triggers an end-to-end build process and verifies success criteria.

3. **Contextual Analysis**: When failures occur, the system uses the vector database to provide contextual information about the failures, potential causes, and recommended actions.

### Running Build Verification

To run the build verification process:

```bash
./run_build_verification.sh
```

Options:
- `--config FILE`: Specify a configuration file (default: verification-config.json)
- `--output FILE`: Specify an output file for the report (default: logs/build_verification_report.json)
- `--skip-analysis`: Skip the relationship analysis step
- `--verbose`: Show verbose output

### CI/CD Integration

The build verification system can be integrated into your CI/CD pipeline using the provided GitHub Actions workflow in `.github/workflows/build-verification.yml`. This workflow automatically runs the build verification process on push to main, pull requests, or manually via workflow dispatch.

## Testing

To run tests for the MCP Codebase Insight project, use the consolidated test runner:

```bash
# Run all tests
python run_tests.py --all

# Run only component tests
python run_tests.py --component

# Run component tests in fully isolated mode (each test in separate process)
python run_tests.py --component --fully-isolated

# Run integration tests
python run_tests.py --integration

# Run with coverage report
python run_tests.py --all --coverage
```

The test suite uses pytest and is organized into:
- **Component Tests**: Test individual components in isolation
- **Integration Tests**: Test components working together
- **API Tests**: Test the API endpoints

### Testing Framework Features

- **Async Fixture Support**: Full support for async fixtures with proper event loop handling
- **Test Isolation**: Option to run tests in fully isolated mode to prevent fixture conflicts
- **Resource Management**: Automatic cleanup of resources after test execution
- **Flexible Configuration**: Configure test settings via environment variables or command line
