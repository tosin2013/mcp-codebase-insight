#!/bin/bash
# This script compiles requirements.in to requirements.txt using pip-compile
# Following the project's build standards for reproducible environments

set -e

# Default Python version if not specified
DEFAULT_VERSION="3.11"
PYTHON_VERSION=${1:-$DEFAULT_VERSION}

# Validate Python version
if [[ ! "$PYTHON_VERSION" =~ ^3\.(9|10|11)$ ]]; then
    echo "Error: Python version must be 3.9, 3.10, or 3.11"
    echo "Usage: $0 [python-version]"
    echo "Example: $0 3.10"
    exit 1
fi

# Set the virtual environment directory based on the Python version
VENV_DIR=".compile-venv-py$PYTHON_VERSION"

echo "=========================================================="
echo "Compiling requirements for Python $PYTHON_VERSION"
echo "=========================================================="

# Create a Python virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a Python $PYTHON_VERSION virtual environment in $VENV_DIR..."
    # Try different ways to create the environment based on the version
    if command -v "python$PYTHON_VERSION" &> /dev/null; then
        "python$PYTHON_VERSION" -m venv "$VENV_DIR"
    elif command -v "python3.$PYTHON_VERSION" &> /dev/null; then
        "python3.$PYTHON_VERSION" -m venv "$VENV_DIR"
    else
        echo "Error: Python $PYTHON_VERSION is not installed."
        echo "Please install it and try again."
        exit 1
    fi
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
if [ -f "requirements-$PYTHON_VERSION.txt" ]; then
    cp "requirements-$PYTHON_VERSION.txt" "requirements-$PYTHON_VERSION.txt.backup"
    echo "Backed up existing requirements-$PYTHON_VERSION.txt to requirements-$PYTHON_VERSION.txt.backup"
fi

# Create a temporary copy of requirements.in with adjusted version constraints
cp requirements.in requirements.in.tmp

# Fix for uvx dependency if needed
echo "Adjusting dependency constraints for compatibility with Python $PYTHON_VERSION..."

# Version-specific adjustments
if [ "$PYTHON_VERSION" = "3.9" ]; then
    # Python 3.9-specific adjustments
    sed -i.bak 's/torch>=2.0.0/torch>=1.13.0,<2.0.0/' requirements.in.tmp 2>/dev/null || sed -i '' 's/torch>=2.0.0/torch>=1.13.0,<2.0.0/' requirements.in.tmp
    sed -i.bak 's/networkx>=.*$/networkx>=2.8.0,<3.0/' requirements.in.tmp 2>/dev/null || sed -i '' 's/networkx>=.*$/networkx>=2.8.0,<3.0/' requirements.in.tmp
elif [ "$PYTHON_VERSION" = "3.10" ]; then
    # Python 3.10-specific adjustments
    sed -i.bak 's/networkx>=.*$/networkx>=2.8.0/' requirements.in.tmp 2>/dev/null || sed -i '' 's/networkx>=.*$/networkx>=2.8.0/' requirements.in.tmp
fi

# Compile requirements.in.tmp to version-specific requirements.txt
echo "Compiling adjusted requirements.in to requirements-$PYTHON_VERSION.txt..."
pip-compile --allow-unsafe --output-file="requirements-$PYTHON_VERSION.txt" requirements.in.tmp

# If that fails, try more conservative approach
if [ $? -ne 0 ]; then
    echo "First compilation attempt failed, trying with more conservative constraints..."
    # Create a more conservative version
    grep -v "uvx\|mcp-server-qdrant" requirements.in > requirements.in.basic
    
    # Add version-specific constraints
    if [ "$PYTHON_VERSION" = "3.9" ]; then
        echo "# Conservative dependencies for Python 3.9" >> requirements.in.basic
        echo "networkx>=2.8.0,<3.0" >> requirements.in.basic
        echo "torch>=1.13.0,<2.0.0" >> requirements.in.basic
    elif [ "$PYTHON_VERSION" = "3.10" ]; then
        echo "# Conservative dependencies for Python 3.10" >> requirements.in.basic
        echo "networkx>=2.8.0" >> requirements.in.basic
    fi
    
    pip-compile --allow-unsafe --output-file="requirements-$PYTHON_VERSION.txt" requirements.in.basic
    echo "NOTE: Some platform-specific dependencies were excluded. You may need to install them separately."
fi

# Create a symlink or copy of the default version to requirements.txt
if [ "$PYTHON_VERSION" = "$DEFAULT_VERSION" ]; then
    echo "Creating requirements.txt as copy of requirements-$PYTHON_VERSION.txt (default version)"
    cp "requirements-$PYTHON_VERSION.txt" requirements.txt
fi

# Clean up temporary files
rm -f requirements.in.tmp requirements.in.tmp.bak requirements.in.bak requirements.in.basic

# Show generated file
echo "Compilation complete. Generated requirements-$PYTHON_VERSION.txt with pinned dependencies."
echo "You can specify a Python version when running this script:"
echo "  ./scripts/compile_requirements.sh 3.9  # For Python 3.9"
echo "  ./scripts/compile_requirements.sh 3.10 # For Python 3.10"
echo "  ./scripts/compile_requirements.sh 3.11 # For Python 3.11"

# Optional: show differences if the file existed before
if [ -f "requirements-$PYTHON_VERSION.txt.backup" ]; then
    echo "Changes from previous requirements-$PYTHON_VERSION.txt:"
    diff -u "requirements-$PYTHON_VERSION.txt.backup" "requirements-$PYTHON_VERSION.txt" || true
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
