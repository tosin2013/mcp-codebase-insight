# Installing MCP Codebase Insight with UVX

This guide explains how to install and use the MCP Codebase Insight project using UVX, a modern Python package manager.

## Prerequisites

1. Python 3.10 or newer
2. Docker (for running Qdrant)
3. UVX package manager

## Installing UVX

UVX is a modern Python package manager that provides improved dependency resolution and installation performance.

```bash
pip install uvx
```

## Setting Up Qdrant for Vector Store

The project requires a Qdrant instance for the vector store functionality:

```bash
docker run -d -p 6333:6333 -p 6334:6334 --name mcp-qdrant qdrant/qdrant
```

## Installing MCP Codebase Insight with UVX

### Option 1: Using the Makefile

The project includes Makefile targets for UVX installation:

```bash
# Install dependencies using UVX
make install-uvx

# Set up development environment with UVX
make dev-setup-uvx
```

### Option 2: Manual Installation

You can also install the project manually with UVX:

```bash
# Install UVX
pip install "uvx<2.0"

# Install in development mode
pip install -e .

# Install with test dependencies
pip install -e ".[test]"

# Install with development dependencies
pip install -e ".[dev]"

# Install with both test and development dependencies
pip install -e ".[test,dev]"
```

## Using UVX Scripts

The project includes predefined scripts in the `uvx.toml` file that you can run with UVX:

```bash
# First, install the project with UVX
pip install "uvx<2.0"
pip install -e .

# Then you can run scripts defined in uvx.toml
# For example, to start the server:
python -m src.mcp_codebase_insight.server

# To start the server in debug mode:
python -m src.mcp_codebase_insight.server --debug

# To run tests:
pytest tests/

# To run tests with coverage:
pytest tests/ --cov=src --cov-report=term-missing
```

## Building with UVX

To build the project using UVX:

```bash
# Using the Makefile
make build-uvx

# Or manually
pip install "uvx<2.0"
pip install build
python -m build
```

## Running the Server

After installation, you can run the server:

```bash
# Using the Makefile
make run

# Using the Makefile with UVX
make run-uvx

# Using Docker (most reliable method)
make run-docker

# Or using Python directly
python -m mcp_codebase_insight.server --debug --port 3000

# Note: The server currently has an issue with the --reload flag
# This is a known issue with the server implementation
```

## Environment Variables

Set these environment variables for proper configuration:

```bash
export QDRANT_URL=http://localhost:6333
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Troubleshooting

If you encounter issues with UVX installation:

1. Make sure you're using Python 3.10 or newer
2. Try updating UVX to the latest version: `pip install --upgrade uvx`
3. If UVX fails to resolve dependencies, you can fall back to pip: `pip install -e ".[test,dev]"`

For server startup issues, ensure:
1. Qdrant is running and accessible at `http://localhost:6333`
2. Environment variables are set properly

## Additional Resources

- [UVX Documentation](https://github.com/microsoft/uvx)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Project README](../../README.md)
