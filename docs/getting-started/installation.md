# Installation Guide

> 🚧 **Documentation In Progress**
> 
> This documentation is being actively developed. More details will be added soon.

## Prerequisites

Before installing MCP Codebase Insight, ensure you have the following:

- Python 3.11 or higher
- pip (Python package installer)
- Git
- Docker (optional, for containerized deployment)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

## System Requirements

### Operating Systems
- Linux (Ubuntu 20.04+, CentOS 8+)
- macOS (10.15+)
- Windows 10/11 with WSL2

### Python Dependencies
- FastAPI
- Pydantic
- httpx
- sentence-transformers
- qdrant-client

## Installation Methods

### 1. Using pip (Recommended)

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install MCP Codebase Insight
pip install mcp-codebase-insight

# Verify installation
mcp-codebase-insight --version
```

### 2. Using Docker

```bash
# Pull the Docker image
docker pull modelcontextprotocol/mcp-codebase-insight

# Create necessary directories
mkdir -p docs knowledge cache

# Run the container
docker run -p 3000:3000 \
    --env-file .env \
    -v $(pwd)/docs:/app/docs \
    -v $(pwd)/knowledge:/app/knowledge \
    -v $(pwd)/cache:/app/cache \
    modelcontextprotocol/mcp-codebase-insight
```

### 3. From Source

```bash
# Clone the repository
git clone https://github.com/modelcontextprotocol/mcp-codebase-insight.git
cd mcp-codebase-insight

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Environment Setup

1. Create a `.env` file in your project root:

```bash
MCP_HOST=127.0.0.1
MCP_PORT=3000
QDRANT_URL=http://localhost:6333
MCP_DOCS_CACHE_DIR=./docs
MCP_ADR_DIR=./docs/adrs
MCP_KB_STORAGE_DIR=./knowledge
MCP_DISK_CACHE_DIR=./cache
LOG_LEVEL=INFO
```

2. Create required directories:

```bash
mkdir -p docs/adrs knowledge cache
```

## Post-Installation Steps

1. **Vector Database Setup**
   - Follow the [Qdrant Setup Guide](qdrant_setup.md) to install and configure Qdrant

2. **Verify Installation**
   ```bash
   # Start the server
   mcp-codebase-insight --host 127.0.0.1 --port 3000
   
   # In another terminal, test the health endpoint
   curl http://localhost:3000/health
   ```

3. **Initial Configuration**
   - Configure authentication (if needed)
   - Set up logging
   - Configure metrics collection

## Common Installation Issues

### 1. Dependencies Installation Fails
```bash
# Try upgrading pip
pip install --upgrade pip

# Install wheel
pip install wheel

# Retry installation
pip install mcp-codebase-insight
```

### 2. Port Already in Use
```bash
# Check what's using port 3000
lsof -i :3000  # On Linux/macOS
netstat -ano | findstr :3000  # On Windows

# Use a different port
mcp-codebase-insight --port 3001
```

### 3. Permission Issues
```bash
# Fix directory permissions
chmod -R 755 docs knowledge cache
```

## Next Steps

- Read the [Configuration Guide](configuration.md) for detailed setup options
- Follow the [Quick Start Tutorial](quickstart.md) to begin using the system
- Check the [Best Practices](../development/best-practices.md) for optimal usage
- Follow the [Qdrant Setup](qdrant_setup.md) to set up the vector database

## Support

If you encounter any issues during installation:

1. Check the [Troubleshooting Guide](../troubleshooting/common-issues.md)
2. Search existing [GitHub Issues](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
3. Open a new issue if needed
