"""
Async Fixture Wrapper for Component Tests

This script serves as a wrapper for running component tests with complex async fixtures
to ensure they are properly awaited in isolated test mode.
"""
import os
import sys
import asyncio
import pytest
import importlib
from pathlib import Path

def run_with_async_fixture_support():
    """Run pytest with proper async fixture support."""
    # Get the module path and test name from command line arguments
    if len(sys.argv) < 3:
        print("Usage: python async_fixture_wrapper.py <module_path> <test_name>")
        sys.exit(1)
    
    module_path = sys.argv[1]
    test_name = sys.argv[2]
    
    # Configure event loop policy for macOS if needed
    if sys.platform == 'darwin':
        import platform
        if int(platform.mac_ver()[0].split('.')[0]) >= 10:
            # macOS 10+ - use the right event loop policy
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    # Ensure PYTHONPATH is set correctly
    base_dir = str(Path(module_path).parent.parent)
    sys.path.insert(0, base_dir)
    
    # Build pytest args
    pytest_args = [module_path, f"-k={test_name}", "--asyncio-mode=strict"]
    
    # Add any additional args
    if len(sys.argv) > 3:
        pytest_args.extend(sys.argv[3:])
    
    # Run the test
    exit_code = pytest.main(pytest_args)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    run_with_async_fixture_support()
