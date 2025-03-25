#!/bin/bash
# This script compiles requirements.in to requirements.txt using pip-compile
# Following the project's build standards for reproducible environments

set -e

VENV_DIR=".compile-venv"

# Create a Python 3.11 virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a Python 3.11 virtual environment in $VENV_DIR..."
    python3.11 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
echo "Activated virtual environment: $VENV_DIR"

# Update pip and setuptools
echo "Updating pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install pip-tools
echo "Installing pip-tools..."
pip install pip-tools

# Make a backup of current requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    cp requirements.txt requirements.txt.backup
    echo "Backed up existing requirements.txt to requirements.txt.backup"
fi

# Create a temporary copy of requirements.in with adjusted version constraints
cp requirements.in requirements.in.tmp

# Fix for uvx dependency that fails with specific error
echo "Adjusting dependency constraints for compatibility..."
# Replace uvx version - the error message suggests it needs v1 on this platform
sed -i.bak 's/uvx>=0.4.0/uvx==1.0.0/' requirements.in.tmp 2>/dev/null || sed -i '' 's/uvx>=0.4.0/uvx==1.0.0/' requirements.in.tmp

# Compile requirements.in.tmp to requirements.txt
echo "Compiling adjusted requirements.in to requirements.txt..."
if ! pip-compile --allow-unsafe --output-file=requirements.txt requirements.in.tmp; then
    echo "First compilation attempt failed, trying with different constraints..."
    # If that fails, try more conservative constraints
    sed -i.bak 's/uvx==1.0.0/uvx==0.4.0/' requirements.in.tmp 2>/dev/null || sed -i '' 's/uvx==1.0.0/uvx==0.4.0/' requirements.in.tmp
    
    # Try without mcp-server-qdrant if needed since it might be causing issues
    if ! pip-compile --allow-unsafe --output-file=requirements.txt requirements.in.tmp; then
        echo "Still having issues, attempting to compile without special dependencies..."
        grep -v "uvx\|mcp-server-qdrant" requirements.in > requirements.in.basic
        pip-compile --allow-unsafe --output-file=requirements.txt requirements.in.basic
        rm requirements.in.basic
        echo "NOTE: Some platform-specific dependencies were excluded. You may need to install them separately."
    fi
fi

# Clean up temporary files
rm -f requirements.in.tmp requirements.in.tmp.bak requirements.in.bak

# Show generated file
echo "Compilation complete. Generated requirements.txt with pinned dependencies."
echo "If you need to update a specific package, use:"
echo "  pip-compile --upgrade-package PACKAGE_NAME requirements.in"

# Optional: show differences if the file existed before
if [ -f "requirements.txt.backup" ]; then
    echo "Changes from previous requirements.txt:"
    diff -u requirements.txt.backup requirements.txt || true
fi

# Deactivate the virtual environment
deactivate
echo "Completed and deactivated virtual environment."

# Clean up the temporary venv if desired
read -p "Remove temporary virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$VENV_DIR"
    echo "Removed temporary virtual environment."
fi

echo "Done."
