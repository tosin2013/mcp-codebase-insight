#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
HOST="127.0.0.1"
PORT="3000"
LOG_LEVEL="INFO"
QDRANT_URL="http://localhost:6333"
COLLECTION="codebase_analysis"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --qdrant-url)
            QDRANT_URL="$2"
            shift 2
            ;;
        --collection)
            COLLECTION="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown argument: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to check if a process is running on a port
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check if Qdrant is running
check_qdrant() {
    if curl -s "$QDRANT_URL/collections" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ -d ".venv" ]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source .venv/bin/activate
    else
        echo -e "${RED}Virtual environment not found. Please run macos_install.sh first.${NC}"
        exit 1
    fi
}

# Function to check Python dependencies
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    if ! pip list | grep -q "qdrant-client"; then
        echo -e "${RED}Dependencies missing. Please run macos_install.sh first.${NC}"
        exit 1
    fi
}

# Function to create required directories
ensure_directories() {
    echo -e "${YELLOW}Ensuring required directories exist...${NC}"
    mkdir -p docs/adrs
    mkdir -p docs/templates
    mkdir -p knowledge/patterns
    mkdir -p references
    mkdir -p logs/debug
}

# Function to check and load environment variables
load_env() {
    if [ -f .env ]; then
        echo -e "${YELLOW}Loading environment variables...${NC}"
        set -a
        source .env
        set +a
    else
        echo -e "${YELLOW}No .env file found, using defaults${NC}"
    fi
}

# Function to start the server
start_server() {
    echo -e "${YELLOW}Starting MCP server...${NC}"
    
    # Export environment variables
    export HOST=$HOST
    export PORT=$PORT
    export LOG_LEVEL=$LOG_LEVEL
    export QDRANT_URL=$QDRANT_URL
    export COLLECTION_NAME=$COLLECTION
    
    # Start server with error handling
    if python -m src.mcp_codebase_insight \
        --host "$HOST" \
        --port "$PORT" \
        --log-level "$LOG_LEVEL" \
        --qdrant-url "$QDRANT_URL" \
        --collection "$COLLECTION"; then
        echo -e "${GREEN}Server started successfully${NC}"
    else
        echo -e "${RED}Failed to start server${NC}"
        exit 1
    fi
}

# Main execution
echo -e "${GREEN}Starting MCP Server Setup...${NC}"

# Check if port is already in use
if check_port "$PORT"; then
    echo -e "${RED}Port $PORT is already in use${NC}"
    exit 1
fi

# Check if Qdrant is running
echo -e "${YELLOW}Checking Qdrant...${NC}"
if ! check_qdrant; then
    echo -e "${YELLOW}Starting Qdrant...${NC}"
    if command -v brew &>/dev/null && brew services list | grep -q qdrant; then
        brew services start qdrant
        
        # Wait for Qdrant to start
        echo "Waiting for Qdrant to start..."
        for i in {1..30}; do
            if check_qdrant; then
                echo "Qdrant is running"
                break
            fi
            if [ $i -eq 30 ]; then
                echo -e "${RED}Qdrant failed to start${NC}"
                exit 1
            fi
            sleep 1
        done
    else
        echo -e "${RED}Qdrant not found. Please run macos_install.sh first.${NC}"
        exit 1
    fi
fi

# Setup environment
activate_venv
check_dependencies
ensure_directories
load_env

# Start server
start_server

# Add trap for cleanup
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    pkill -f "python -m src.mcp_codebase_insight" || true
}
trap cleanup EXIT

# Keep script running to handle signals
while true; do
    sleep 1
done
