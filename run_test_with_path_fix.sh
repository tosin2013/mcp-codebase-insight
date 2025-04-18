#!/bin/bash
# This script runs tests with a fix for the Python path issue

set -e

# Activate the virtual environment
source .venv/bin/activate

# Setup environment for Qdrant
export MCP_TEST_MODE=1
export QDRANT_URL="http://localhost:6333"
export MCP_COLLECTION_NAME="test_collection_$(date +%s)"
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Initialize Qdrant collection for testing
echo "Creating Qdrant collection for testing..."
python - << EOF
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Connect to Qdrant
client = QdrantClient(url="http://localhost:6333")
collection_name = os.environ.get("MCP_COLLECTION_NAME")

# Check if collection exists
collections = client.get_collections().collections
collection_names = [c.name for c in collections]

if collection_name in collection_names:
    print(f"Collection {collection_name} already exists, recreating it...")
    client.delete_collection(collection_name=collection_name)

# Create collection with vector size 384 (for all-MiniLM-L6-v2)
client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=384,  # Dimension for all-MiniLM-L6-v2
        distance=models.Distance.COSINE,
    ),
)

# Create test directory that might be needed
os.makedirs("qdrant_storage", exist_ok=True)

print(f"Successfully created collection {collection_name}")
EOF

# Run all component tests in vector_store
echo "Running all vector store tests with component_test_runner.py..."
python component_test_runner.py tests/components/test_vector_store.py
