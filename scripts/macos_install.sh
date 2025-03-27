#!/bin/bash

# Exit on error
set -e

echo "Installing MCP Codebase Insight development environment..."

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew already installed, updating..."
    brew update
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    brew install python@3.11
else
    echo "Python already installed"
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    brew install --cask docker
    
    echo "Starting Docker..."
    open -a Docker
    
    # Wait for Docker to start
    echo "Waiting for Docker to start..."
    while ! docker info &> /dev/null; do
        sleep 1
    done
else
    echo "Docker already installed"
fi

# Create virtual environment
echo "Creating virtual environment..."
python3.11 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start Qdrant
echo "Starting Qdrant container..."
if ! docker ps | grep -q qdrant; then
    docker run -d -p 6333:6333 -p 6334:6334 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        qdrant/qdrant
    echo "Qdrant container started"
else
    echo "Qdrant container already running"
fi

# Create required directories
echo "Creating project directories..."
mkdir -p docs/adrs
mkdir -p docs/templates
mkdir -p knowledge/patterns
mkdir -p references
mkdir -p logs/debug

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env with your settings"
fi

# Load example patterns
echo "Loading example patterns..."
python scripts/load_example_patterns.py

echo "
Installation complete! 🎉

To start development:
1. Update .env with your settings
2. Activate the virtual environment:
   source .venv/bin/activate
3. Start the server:
   make run

For more information, see the README.md file.
"
