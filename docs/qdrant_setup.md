# Qdrant Setup Guide

## Overview
This document outlines the setup and maintenance procedures for the Qdrant vector database instance required for running tests and development.

## Prerequisites
- Docker installed and running
- Port 6333 available on localhost
- Python 3.8+ with pip

## Setup Options

### Option 1: Docker Container (Recommended for Development)
```bash
# Pull the latest Qdrant image
docker pull qdrant/qdrant:latest

# Run Qdrant container
docker run -d \
  --name mcp-qdrant \
  -p 6333:6333 \
  -v $(pwd)/qdrant_data:/qdrant/storage \
  qdrant/qdrant

# Verify the instance is running
curl http://localhost:6333/health
```

### Option 2: Pre-existing Instance
If using a pre-existing Qdrant instance:
1. Ensure it's accessible at `localhost:6333`
2. Verify health status
3. Configure environment variables if needed:
```bash
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
```

## Health Check
```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
health = client.health()
print(f"Qdrant health status: {health}")
```

## Maintenance
- Regular health checks are automated in CI/CD pipeline
- Database backups are stored in `./qdrant_data`
- Version updates should be coordinated with the team

## Troubleshooting
1. If container fails to start:
   ```bash
   # Check logs
   docker logs mcp-qdrant
   
   # Verify port availability
   lsof -i :6333
   ```

2. If connection fails:
   ```bash
   # Restart container
   docker restart mcp-qdrant
   
   # Check container status
   docker ps -a | grep mcp-qdrant
   ```

## Responsible Parties
- Primary maintainer: DevOps Team
- Documentation updates: Development Team Lead
- Testing coordination: QA Team Lead

## Version Control
- Document version: 1.0
- Last updated: 2025-03-24
- Next review: 2025-06-24
