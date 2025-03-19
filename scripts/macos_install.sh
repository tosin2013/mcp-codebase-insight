#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting MCP Server Setup...${NC}"

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
if command -v python3.11 &>/dev/null; then
    echo "Python 3.11 found"
else
    echo -e "${RED}Python 3.11 not found. Installing via Homebrew...${NC}"
    if ! command -v brew &>/dev/null; then
        echo -e "${RED}Homebrew not found. Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python@3.11
fi

# Create virtual environment
echo -e "\n${YELLOW}Setting up virtual environment...${NC}"
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
python -m pip install --upgrade pip
pip install -e ".[dev]"

# Check Docker and Qdrant container
echo -e "\n${YELLOW}Checking Docker and Qdrant...${NC}"
if ! command -v docker &>/dev/null; then
    echo -e "${RED}Docker not found. Please install Docker Desktop from https://www.docker.com/products/docker-desktop${NC}"
    exit 1
fi

# Check if Qdrant container is running
if ! docker ps | grep -q qdrant/qdrant; then
    echo -e "${YELLOW}Qdrant container not found. Please ensure it's running with:${NC}"
    echo -e "docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:consistent qdrant/qdrant:latest"
    exit 1
fi

# Create required directories
echo -e "\n${YELLOW}Creating required directories...${NC}"
mkdir -p docs/adrs
mkdir -p docs/templates
mkdir -p knowledge/patterns
mkdir -p references
mkdir -p logs/debug

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env file...${NC}"
    cat > .env << EOL
# Server settings
HOST=127.0.0.1
PORT=3000
LOG_LEVEL=INFO

# Qdrant settings (Docker)
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=codebase_analysis

# Cache settings
CACHE_ENABLED=true
CACHE_SIZE=1000
CACHE_TTL=3600

# Documentation settings
DOCS_CACHE_DIR=references
DOCS_REFRESH_INTERVAL=86400
DOCS_MAX_SIZE=1000000

# Knowledge base settings
KB_STORAGE_DIR=knowledge
KB_BACKUP_INTERVAL=86400
KB_MAX_PATTERNS=10000
EOL
fi

# Update .gitignore
echo -e "\n${YELLOW}Updating .gitignore...${NC}"
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Project specific
references/
knowledge/
logs/
*.cache
*.log
qdrant_storage/

# macOS
.DS_Store
.AppleDouble
.LSOverride
._*
EOL

# Create example ADR template if it doesn't exist
if [ ! -f docs/templates/adr.md ]; then
    echo -e "\n${YELLOW}Creating ADR template...${NC}"
    cp docs/templates/adr.md.example docs/templates/adr.md
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\nTo start the server:"
echo -e "1. Activate the virtual environment: ${YELLOW}source .venv/bin/activate${NC}"
echo -e "2. Run the server: ${YELLOW}python -m src.mcp_server_qdrant${NC}"
echo -e "\nQdrant UI is available at: ${YELLOW}http://localhost:6333/dashboard${NC}"
echo -e "Server documentation will be available at: ${YELLOW}http://localhost:3000/docs${NC}"
