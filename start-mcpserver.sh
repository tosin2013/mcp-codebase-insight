#!/bin/bash
# This script starts the MCP Qdrant server with SSE transport
set -x
source .venv/bin/activate
# Set the PATH to include the local bin directory
export PATH="$HOME/.local/bin:$PATH"

# Define environment variables
export COLLECTION_NAME="mcp-codebase-insight"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
export QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzQ1MTAyNzQ3fQ.3gvK8M7dJxZkSpyzpJtTGVUhjyjgbYEhEvl2aG7JodM"

# Define tool descriptions
TOOL_STORE_DESCRIPTION="Store reusable code snippets and test results. 'information' contains a description. 'metadata' is a dictionary with a 'type' key: 'code' for code snippets, 'test_result' for test results. For 'code', 'metadata' includes a 'code' key with the code. For 'test_result', 'metadata' includes 'test_name', 'status' (pass/fail), and 'error_message'."

TOOL_FIND_DESCRIPTION="Search for code snippets and test results. The 'query' parameter describes what you're looking for. Returned results will have a 'metadata' field with a 'type' key indicating 'code' or 'test_result'. Use this to find code or analyze test failures."

# Run the MCP Qdrant server with SSE transport
uvx mcp-server-qdrant --transport sse
