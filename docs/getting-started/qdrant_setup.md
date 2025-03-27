# Qdrant Setup Guide

> 🚧 **Documentation In Progress**
> 
> This documentation is being actively developed. More details will be added soon.

## Overview

This guide covers setting up Qdrant vector database for MCP Codebase Insight.

## Installation Methods

### 1. Using Docker (Recommended)

```bash
# Pull the Qdrant image
docker pull qdrant/qdrant

# Start Qdrant container
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 2. From Binary

Download from [Qdrant Releases](https://github.com/qdrant/qdrant/releases)

### 3. From Source

```bash
git clone https://github.com/qdrant/qdrant
cd qdrant
cargo build --release
```

## Configuration

1. **Create Collection**
   ```python
   from qdrant_client import QdrantClient
   
   client = QdrantClient("localhost", port=6333)
   client.create_collection(
       collection_name="code_vectors",
       vectors_config={"size": 384, "distance": "Cosine"}
   )
   ```

2. **Verify Setup**
   ```bash
   curl http://localhost:6333/collections/code_vectors
   ```

## Next Steps

- [Configuration Guide](configuration.md)
- [Quick Start Guide](quickstart.md)
- [API Reference](../api/rest-api.md) 