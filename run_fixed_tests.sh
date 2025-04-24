#!/bin/bash
# This script runs tests with proper path and environment setup

set -e

# Activate the virtual environment
source .venv/bin/activate

# Install the package in development mode
pip install -e .

# Set environment variables
export MCP_TEST_MODE=1
export QDRANT_URL="http://localhost:6333"
export MCP_COLLECTION_NAME="test_collection_$(date +%s)"
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Check if we should run a specific test or all tests
if [ $# -eq 0 ]; then
  echo "Running specific vector store tests..."
  python component_test_runner.py tests/components/test_vector_store.py
else
  echo "Running specified tests: $*"
  python component_test_runner.py "$@"
fi
