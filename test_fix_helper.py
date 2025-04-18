#!/usr/bin/env python3
"""
A utility script to help fix common test issues in the MCP Codebase Insight project.
This script can:
1. Update import paths in all test files
2. Check for proper dependencies
3. Set up proper Python path in conftest.py files
"""

import os
import re
import sys
import importlib
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def add_python_path_to_conftest(conftest_path: str) -> bool:
    """Add Python path setting to a conftest.py file."""
    if not os.path.exists(conftest_path):
        print(f"Error: {conftest_path} does not exist")
        return False

    with open(conftest_path, 'r') as f:
        content = f.read()

    # Check if Python path is already set
    if "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))" in content:
        print(f"Python path already set in {conftest_path}")
        return True

    # Add import statements if needed
    imports_to_add = []
    if "import sys" not in content:
        imports_to_add.append("import sys")
    if "import os" not in content:
        imports_to_add.append("import os")

    # Find a good spot to insert the path setting (after imports)
    lines = content.split('\n')
    insert_position = 0
    
    # Find the last import statement
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_position = i + 1

    # Insert the Python path setting
    path_setting = "\n# Ensure the src directory is in the Python path\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))\n"
    
    # Add imports if needed
    if imports_to_add:
        path_setting = "\n" + "\n".join(imports_to_add) + path_setting

    # Insert into content
    new_content = '\n'.join(lines[:insert_position]) + path_setting + '\n'.join(lines[insert_position:])

    # Write back to file
    with open(conftest_path, 'w') as f:
        f.write(new_content)

    print(f"Added Python path setting to {conftest_path}")
    return True


def fix_imports_in_file(file_path: str) -> Tuple[int, int]:
    """Fix import paths in a Python file, changing from 'mcp_codebase_insight' to 'src.mcp_codebase_insight'."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with a different encoding or skip the file
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return 0, 0

    # Look for the problematic imports
    pattern = r'from\s+mcp_codebase_insight\.'
    matches = re.findall(pattern, content)
    if not matches:
        return 0, 0  # No matches found

    # Replace with correct import path
    new_content = re.sub(pattern, 'from src.mcp_codebase_insight.', content)
    
    # Add sys.path.insert if not already present and there were matches
    if 'sys.path.insert' not in new_content:
        import_sys_path = (
            "import sys\n"
            "import os\n\n"
            "# Ensure the src directory is in the Python path\n"
            "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))\n\n"
        )
        
        # Find a good spot to insert the path setting (before imports)
        lines = new_content.split('\n')
        insert_position = 0
        
        # Find the first import statement
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_position = i
                break
        
        # Reconstruct the content with path inserted
        new_content = '\n'.join(lines[:insert_position]) + '\n' + import_sys_path + '\n'.join(lines[insert_position:])

    # Write the changes back to the file with the same encoding we used to read it
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except UnicodeEncodeError:
        with open(file_path, 'w', encoding='latin-1') as f:
            f.write(new_content)

    return len(matches), 1  # Return number of replacements and files modified


def find_and_fix_test_files(root_dir: str = '.') -> Tuple[int, int]:
    """Find all test files in the project and fix their imports."""
    test_files = []
    conftest_files = []

    # Walk through the directory structure to find test files
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
            elif file == 'conftest.py':
                conftest_files.append(os.path.join(root, file))

    # Fix imports in all test files
    total_replacements = 0
    total_files_modified = 0

    for file_path in test_files:
        replacements, files_modified = fix_imports_in_file(file_path)
        total_replacements += replacements
        total_files_modified += files_modified
        if replacements > 0:
            print(f"Fixed {replacements} imports in {file_path}")

    # Update conftest files
    for conftest_path in conftest_files:
        if add_python_path_to_conftest(conftest_path):
            total_files_modified += 1

    return total_replacements, total_files_modified


def check_dependencies() -> bool:
    """Check if all required dependencies are installed."""
    required_packages = [
        'sentence-transformers',
        'torch',
        'fastapi',
        'qdrant-client',
        'pytest',
        'pytest-asyncio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is NOT installed")
    
    if missing_packages:
        print("\nMissing packages:")
        for package in missing_packages:
            print(f"- {package}")
        return False
    
    return True


def install_dependencies() -> bool:
    """Install missing dependencies."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies from requirements.txt")
        return False


def create_path_fix_script() -> bool:
    """Create a script to fix path issues when running tests."""
    script_content = """#!/bin/bash
# This script runs tests with proper path and environment setup

set -e

# Activate the virtual environment (or create it if it doesn't exist)
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install required dependencies
echo "Installing required dependencies..."
pip install -e .
pip install pytest pytest-asyncio

# Set environment variables
export MCP_TEST_MODE=1
export QDRANT_URL="http://localhost:6333"
export MCP_COLLECTION_NAME="test_collection_$(date +%s)"
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run the tests
echo "Running tests..."
python -m pytest "$@"
"""
    
    script_path = 'run_fixed_tests.sh'
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    print(f"Created {script_path} - use it to run tests with proper path setup")
    return True


def main():
    """Main entry point."""
    print("=== MCP Codebase Insight Test Fix Helper ===\n")
    
    # Find and fix import issues
    print("Fixing import paths in test files...")
    replacements, files_modified = find_and_fix_test_files()
    print(f"Fixed {replacements} imports in {files_modified} files\n")
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("\nWould you like to install missing dependencies? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            install_dependencies()
    
    # Create helper script
    print("\nCreating test runner script...")
    create_path_fix_script()
    
    print("\n=== Fixes Complete ===")
    print("""
Next steps:
1. Run the tests using: ./run_fixed_tests.sh [test_options]
   e.g., ./run_fixed_tests.sh tests/components/test_vector_store.py -v

2. If Qdrant collection creation fails, check the Docker container:
   docker run -d -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant

3. If specific tests still fail, check their requirements individually
""")


if __name__ == "__main__":
    main()
