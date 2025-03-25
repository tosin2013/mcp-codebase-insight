# Docker Setup Guide

This guide covers how to set up and run MCP Codebase Insight using Docker.

## Prerequisites

- Docker installed on your system
- Basic knowledge of Docker commands
- Qdrant vector database accessible from your Docker network (required)

## Running Qdrant Container

MCP Codebase Insight requires a running Qdrant instance. Make sure to start Qdrant before running the MCP container:

```bash
# Create a directory for Qdrant data
mkdir -p qdrant_data

# Pull and run Qdrant container
docker pull qdrant/qdrant
docker run -d --name qdrant \
    -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_data:/qdrant/storage \
    qdrant/qdrant
```

You can access the Qdrant web UI at http://localhost:6334 to verify it's running correctly.

## Quick Start with Docker

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

## Creating a .env File for Docker

Create a `.env` file in your project directory with the following content:

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

## Volume Mounts

The Docker command mounts several directories from your host system into the container:

- `$(pwd)/docs:/app/docs`: Maps your local docs directory to the container's docs directory
- `$(pwd)/knowledge:/app/knowledge`: Maps your local knowledge directory to the container's knowledge directory

Make sure these directories exist on your host system before running the container:

```bash
mkdir -p docs/adrs knowledge
```

## Using Docker Compose

For a more manageable setup, you can use Docker Compose. Create a `docker-compose.yml` file in your project directory:

```yaml
version: '3'

services:
  mcp-codebase-insight:
    image: tosin2013/mcp-codebase-insight
    ports:
      - "3000:3000"
    volumes:
      - ./docs:/app/docs
      - ./knowledge:/app/knowledge
      - ./cache:/app/cache
    env_file:
      - .env
    networks:
      - mcp-network

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/storage
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

Then start the services:

```bash
docker-compose up -d
```

## Advanced Docker Configuration

### Using Custom Embedding Models

To use a custom embedding model, add the model path to your volume mounts and update the environment configuration:

```bash
docker run -p 3000:3000 \
    --env-file .env \
    -v $(pwd)/docs:/app/docs \
    -v $(pwd)/knowledge:/app/knowledge \
    -v $(pwd)/models:/app/models \
    -e MCP_EMBEDDING_MODEL=/app/models/custom-model \
    tosin2013/mcp-codebase-insight
```

### Securing Your Docker Deployment

For production environments:

1. Use Docker networks to isolate the MCP and Qdrant services
2. Don't expose the Qdrant port to the public internet
3. Set up proper authentication for both services
4. Use Docker secrets for sensitive information
5. Consider using a reverse proxy with HTTPS for the API

## Troubleshooting Docker Issues

### Connection Refused to Qdrant

If you're getting connection errors to Qdrant, check:

- Is Qdrant running? (`docker ps | grep qdrant`)
- Is the URL correct in the `.env` file?
- Are both services on the same Docker network?
- Try using the service name instead of `host.docker.internal` if using Docker Compose

### Container Exits Immediately

If the container exits immediately:

- Check the Docker logs: `docker logs <container_id>`
- Ensure all required environment variables are set
- Verify that the mounted directories have correct permissions

### Out of Memory Errors

If you encounter out of memory errors:

- Increase the memory limit for the container
- Reduce the vector dimension or batch size in your configuration
- Consider using a more efficient embedding model
