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

# Check for private repository configuration
PRIVATE_REPO_URL=${PRIVATE_REPO_URL:-""}
PRIVATE_REPO_TOKEN=${PRIVATE_REPO_TOKEN:-""}

# Check for local package paths (comma-separated list of directories)
LOCAL_PACKAGE_PATHS=${LOCAL_PACKAGE_PATHS:-""}

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

# Create pip.conf for private repository access if provided
if [ ! -z "$PRIVATE_REPO_URL" ]; then
    mkdir -p "$VENV_DIR/pip"
    cat > "$VENV_DIR/pip/pip.conf" << EOF
[global]
index-url = https://pypi.org/simple
extra-index-url = ${PRIVATE_REPO_URL}
EOF
    
    if [ ! -z "$PRIVATE_REPO_TOKEN" ]; then
        echo "Using private repository with authentication token"
        # Add credentials to pip.conf if token is provided
        sed -i.bak "s|${PRIVATE_REPO_URL}|${PRIVATE_REPO_URL}:${PRIVATE_REPO_TOKEN}@|" "$VENV_DIR/pip/pip.conf" 2>/dev/null || \
        sed -i '' "s|${PRIVATE_REPO_URL}|${PRIVATE_REPO_URL}:${PRIVATE_REPO_TOKEN}@|" "$VENV_DIR/pip/pip.conf"
    fi
    
    export PIP_CONFIG_FILE="$VENV_DIR/pip/pip.conf"
fi

# Parse and set up local package paths if provided
LOCAL_ARGS=""
if [ ! -z "$LOCAL_PACKAGE_PATHS" ]; then
    echo "Setting up local package paths..."
    IFS=',' read -ra PATHS <<< "$LOCAL_PACKAGE_PATHS"
    for path in "${PATHS[@]}"; do
        LOCAL_ARGS="$LOCAL_ARGS -f $path"
    done
    echo "Local package paths: $LOCAL_ARGS"
fi

# Check for local git repositories
if [ -d "./local-packages" ]; then
    echo "Found local-packages directory, will include in search path"
    LOCAL_ARGS="$LOCAL_ARGS -f ./local-packages"
fi

# Fix for dependency issues - version-specific adjustments
echo "Adjusting dependency constraints for compatibility with Python $PYTHON_VERSION..."

# Version-specific adjustments
if [ "$PYTHON_VERSION" = "3.9" ]; then
    # Python 3.9-specific adjustments
    sed -i.bak 's/torch>=2.0.0/torch>=1.13.0,<2.0.0/' requirements.in.tmp 2>/dev/null || sed -i '' 's/torch>=2.0.0/torch>=1.13.0,<2.0.0/' requirements.in.tmp
    sed -i.bak 's/networkx>=.*$/networkx>=2.8.0,<3.0/' requirements.in.tmp 2>/dev/null || sed -i '' 's/networkx>=.*$/networkx>=2.8.0,<3.0/' requirements.in.tmp
    # Keep starlette constraint for Python 3.9
elif [ "$PYTHON_VERSION" = "3.10" ] || [ "$PYTHON_VERSION" = "3.11" ]; then
    # Python 3.10/3.11-specific adjustments
    sed -i.bak 's/networkx>=.*$/networkx>=2.8.0/' requirements.in.tmp 2>/dev/null || sed -i '' 's/networkx>=.*$/networkx>=2.8.0/' requirements.in.tmp
    
    # Modify starlette constraint for Python 3.10/3.11 (for diagnostic purposes)
    echo "Modifying starlette constraint for Python $PYTHON_VERSION to diagnose dependency conflicts..."
    sed -i.bak 's/starlette>=0.27.0,<0.28.0/starlette>=0.27.0/' requirements.in.tmp 2>/dev/null || \
    sed -i '' 's/starlette>=0.27.0,<0.28.0/starlette>=0.27.0/' requirements.in.tmp
    
    # Diagnostic output to verify the change
    echo "Modified starlette constraint in requirements.in.tmp:"
    grep "starlette" requirements.in.tmp || echo "No starlette constraint found"
fi

# Special handling for private packages
COMPILE_SUCCESS=0

# Try to compile with all packages
echo "Compiling adjusted requirements.in to requirements-$PYTHON_VERSION.txt..."
if pip-compile --allow-unsafe $LOCAL_ARGS --output-file="requirements-$PYTHON_VERSION.txt" requirements.in.tmp; then
    COMPILE_SUCCESS=1
    echo "Compilation successful with all packages included."
else
    echo "First compilation attempt failed, trying without private packages..."
fi

# If compilation with all packages failed, try without problematic private packages
if [ $COMPILE_SUCCESS -eq 0 ]; then
    echo "Creating a version without private packages..."
    grep -v "uvx\|mcp-server-qdrant" requirements.in > requirements.in.basic
    
    # Add version-specific constraints
    if [ "$PYTHON_VERSION" = "3.9" ]; then
        echo "# Conservative dependencies for Python 3.9" >> requirements.in.basic
        echo "networkx>=2.8.0,<3.0" >> requirements.in.basic
        echo "torch>=1.13.0,<2.0.0" >> requirements.in.basic
        # Keep original starlette constraint
        grep "starlette" requirements.in >> requirements.in.basic
    elif [ "$PYTHON_VERSION" = "3.10" ] || [ "$PYTHON_VERSION" = "3.11" ]; then
        echo "# Conservative dependencies for Python $PYTHON_VERSION" >> requirements.in.basic
        echo "networkx>=2.8.0" >> requirements.in.basic
        # Modified starlette constraint for 3.10/3.11
        echo "starlette>=0.27.0" >> requirements.in.basic
    fi
    
    if pip-compile --allow-unsafe $LOCAL_ARGS --output-file="requirements-$PYTHON_VERSION.txt" requirements.in.basic; then
        COMPILE_SUCCESS=1
        echo "Compilation successful without private packages."
        echo "# NOTE: Private packages (uvx, mcp-server-qdrant) were excluded from this compilation." >> "requirements-$PYTHON_VERSION.txt"
        echo "# You may need to install them separately from their source." >> "requirements-$PYTHON_VERSION.txt"
        
        # Create a separate file just for private packages
        echo "# Private packages excluded from main requirements-$PYTHON_VERSION.txt" > "requirements-private-$PYTHON_VERSION.txt"
        grep "uvx\|mcp-server-qdrant" requirements.in >> "requirements-private-$PYTHON_VERSION.txt"
        echo "Created separate requirements-private-$PYTHON_VERSION.txt for private packages."
    else
        echo "WARNING: Both compilation attempts failed. Please check for compatibility issues."
        # Additional diagnostic information
        echo "Failed compilation error log:"
        if [ "$PYTHON_VERSION" = "3.10" ] || [ "$PYTHON_VERSION" = "3.11" ]; then
            echo "Testing if removing starlette constraint entirely resolves the issue..."
            grep -v "starlette\|uvx\|mcp-server-qdrant" requirements.in > requirements.in.minimal
            echo "# Minimal dependencies for Python $PYTHON_VERSION" >> requirements.in.minimal
            echo "networkx>=2.8.0" >> requirements.in.minimal
            
            if pip-compile --allow-unsafe $LOCAL_ARGS --output-file="requirements-$PYTHON_VERSION.minimal.txt" requirements.in.minimal; then
                echo "SUCCESS: Compilation successful without starlette constraint."
                echo "This confirms that starlette is causing dependency conflicts."
                # Create a working requirements file for now
                mv "requirements-$PYTHON_VERSION.minimal.txt" "requirements-$PYTHON_VERSION.txt"
                echo "# WARNING: starlette constraint was removed to resolve conflicts" >> "requirements-$PYTHON_VERSION.txt"
                echo "# You will need to manually install a compatible starlette version" >> "requirements-$PYTHON_VERSION.txt"
                COMPILE_SUCCESS=1
            else
                echo "FAILURE: Issue persists even without starlette constraint."
            fi
        fi
    fi
fi

# Create a symlink or copy of the default version to requirements.txt
if [ "$PYTHON_VERSION" = "$DEFAULT_VERSION" ]; then
    echo "Creating requirements.txt as copy of requirements-$PYTHON_VERSION.txt (default version)"
    cp "requirements-$PYTHON_VERSION.txt" requirements.txt
    
    # Also copy private requirements if they exist
    if [ -f "requirements-private-$PYTHON_VERSION.txt" ]; then
        cp "requirements-private-$PYTHON_VERSION.txt" requirements-private.txt
    fi
fi

# Clean up temporary files
rm -f requirements.in.tmp requirements.in.tmp.bak requirements.in.bak requirements.in.basic requirements.in.minimal 2>/dev/null || true

# Show generated file
echo "Compilation complete. Generated requirements-$PYTHON_VERSION.txt with pinned dependencies."
echo ""
echo "To use private package repositories, set environment variables before running this script:"
echo "  export PRIVATE_REPO_URL=\"https://your-private-repo.com/simple\""
echo "  export PRIVATE_REPO_TOKEN=\"your-access-token\"  # Optional"
echo ""
echo "To use local package paths, set LOCAL_PACKAGE_PATHS:"
echo "  export LOCAL_PACKAGE_PATHS=\"/path/to/packages1,/path/to/packages2\""
echo ""
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
