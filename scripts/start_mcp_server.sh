#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if Qdrant is available
check_qdrant() {
    local url="${QDRANT_URL:-http://localhost:6333}"
    local max_attempts=30
    local attempt=1

    log "Checking Qdrant connection at $url"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url/health" > /dev/null 2>&1; then
            log "Qdrant is available"
            return 0
        fi
        
        log "Waiting for Qdrant (attempt $attempt/$max_attempts)..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log "Error: Could not connect to Qdrant"
    return 1
}

# Function to check Python environment
check_python() {
    if ! command -v python3 &> /dev/null; then
        log "Error: Python 3 is not installed"
        exit 1
    fi
    
    if ! python3 -c "import pkg_resources; pkg_resources.require('fastapi>=0.103.2')" &> /dev/null; then
        log "Error: Required Python packages are not installed"
        exit 1
    fi
}

# Function to setup environment
setup_env() {
    # Create required directories if they don't exist
    mkdir -p docs/adrs knowledge cache logs
    
    # Copy example env file if .env doesn't exist
    if [ ! -f .env ] && [ -f .env.example ]; then
        cp .env.example .env
        log "Created .env from example"
    fi
    
    # Set default environment variables if not set
    export MCP_HOST=${MCP_HOST:-0.0.0.0}
    export MCP_PORT=${MCP_PORT:-3000}
    export MCP_LOG_LEVEL=${MCP_LOG_LEVEL:-INFO}
    
    log "Environment setup complete"
}

# Main startup sequence
main() {
    log "Starting MCP Codebase Insight Server"
    
    # Perform checks
    check_python
    setup_env
    check_qdrant
    
    # Parse command line arguments
    local host="0.0.0.0"
    local port="3000"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --host)
                host="$2"
                shift 2
                ;;
            --port)
                port="$2"
                shift 2
                ;;
            *)
                log "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Start server
    log "Starting server on $host:$port"
    exec python3 -m mcp_codebase_insight
}

# Run main function with all arguments
main "$@"
