#!/bin/bash
# Script to check if Qdrant service is available and healthy
# Usage: ./check_qdrant_health.sh [qdrant_url] [max_retries] [sleep_seconds]

# Default values
QDRANT_URL=${1:-"http://localhost:6333"}
MAX_RETRIES=${2:-20}
SLEEP_SECONDS=${3:-5}

echo "Checking Qdrant health at $QDRANT_URL (max $MAX_RETRIES attempts with $SLEEP_SECONDS seconds delay)"

# Install dependencies if not present
if ! command -v curl &> /dev/null || ! command -v jq &> /dev/null; then
    echo "Installing required dependencies..."
    apt-get update &> /dev/null && apt-get install -y curl jq &> /dev/null || true
fi

# Check if dependencies are available
if ! command -v curl &> /dev/null; then
    echo "Error: curl command not found and could not be installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Warning: jq command not found and could not be installed. JSON validation will be skipped."
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Wait for Qdrant to be available
retry_count=0
until [ $(curl -s -o /dev/null -w "%{http_code}" $QDRANT_URL/collections) -eq 200 ] || [ $retry_count -eq $MAX_RETRIES ]
do
    echo "Waiting for Qdrant... (attempt $retry_count of $MAX_RETRIES)"
    sleep $SLEEP_SECONDS
    retry_count=$((retry_count+1))
done

if [ $retry_count -eq $MAX_RETRIES ]; then
    echo "Qdrant service failed to become available after $((MAX_RETRIES * SLEEP_SECONDS)) seconds"
    exit 1
fi

# Check for valid JSON response if jq is available
if [ "$JQ_AVAILABLE" = true ]; then
    if ! curl -s $QDRANT_URL/collections | jq . > /dev/null; then
        echo "Qdrant did not return valid JSON."
        exit 1
    fi
fi

echo "Qdrant service is accessible and healthy."
exit 0 