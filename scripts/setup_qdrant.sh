#!/bin/bash

# Script to set up Qdrant for MCP Codebase Insight
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Setting up Qdrant for MCP Codebase Insight..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if port 6333 is available
if lsof -Pi :6333 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}Warning: Port 6333 is already in use${NC}"
    echo "Checking if it's a Qdrant instance..."
    if curl -s http://localhost:6333/health > /dev/null; then
        echo -e "${GREEN}Existing Qdrant instance detected and healthy${NC}"
        exit 0
    else
        echo -e "${RED}Port 6333 is in use by another service${NC}"
        exit 1
    fi
fi

# Create data directory if it doesn't exist
mkdir -p ./qdrant_data

# Stop and remove existing container if it exists
if docker ps -a | grep -q mcp-qdrant; then
    echo "Removing existing mcp-qdrant container..."
    docker stop mcp-qdrant || true
    docker rm mcp-qdrant || true
fi

# Pull latest Qdrant image
echo "Pulling latest Qdrant image..."
docker pull qdrant/qdrant:latest

# Start Qdrant container
echo "Starting Qdrant container..."
docker run -d \
    --name mcp-qdrant \
    -p 6333:6333 \
    -v "$(pwd)/qdrant_data:/qdrant/storage" \
    qdrant/qdrant

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:6333/health > /dev/null; then
        echo -e "${GREEN}Qdrant is ready!${NC}"
        exit 0
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

echo -e "${RED}Error: Qdrant failed to start within 30 seconds${NC}"
exit 1
