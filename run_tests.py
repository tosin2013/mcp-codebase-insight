#!/usr/bin/env python3
"""
Test runner script for MCP Codebase Insight.

This script consolidates all test execution into a single command with various options.
It can run specific test categories or all tests, with or without coverage reporting.
"""

import argparse
import os
import subprocess
import sys
import time
from typing import List, Optional
import uuid
import traceback


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run MCP Codebase Insight tests")
    
    # Test selection options
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--component", action="store_true", help="Run component tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--config", action="store_true", help="Run configuration tests")
    parser.add_argument("--api", action="store_true", help="Run API endpoint tests")
    
    # Specific test selection
    parser.add_argument("--test", type=str, help="Run a specific test (e.g., test_health_check)")
    parser.add_argument("--file", type=str, help="Run tests from a specific file")
    
    # Coverage options
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    
    # Additional options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-capture", action="store_true", help="Don't capture stdout/stderr")
    parser.add_argument("--clean", action="store_true", help="Clean .pytest_cache before running tests")
    parser.add_argument("--isolated", action="store_true", help="Run with PYTHONPATH isolated to ensure clean environment")
    parser.add_argument("--event-loop-debug", action="store_true", help="Add asyncio debug mode")
    parser.add_argument("--sequential", action="store_true", help="Run tests sequentially to avoid event loop issues")
    parser.add_argument("--fully-isolated", action="store_true", 
                       help="Run each test module in a separate process for complete isolation")
    
    return parser.parse_args()


def build_command(args, module_path=None) -> List[List[str]]:
    """Build the pytest command based on arguments."""
    cmd = ["python", "-m", "pytest"]
    
    # Add xdist settings for parallel or sequential execution
    if args.sequential:
        # Run sequentially to avoid event loop issues
        os.environ["PYTEST_XDIST_AUTO_NUM_WORKERS"] = "1"
        cmd.append("-xvs")
    
    # Determine test scope
    test_paths = []
    
    # If a specific module path is provided, use it
    if module_path:
        test_paths.append(module_path)
    elif args.all or (not any([args.component, args.integration, args.config, args.api, args.test, args.file])):
        # When running all tests and using fully isolated mode, we'll handle this differently in main()
        if args.fully_isolated:
            return []
        
        # When running all tests, run integration tests separately from other tests
        if args.all and not args.sequential:
            # Run integration tests separately to avoid event loop conflicts
            integration_cmd = cmd.copy()
            integration_cmd.append("tests/integration/")
            non_integration_cmd = cmd.copy()
            non_integration_cmd.append("tests/")
            non_integration_cmd.append("--ignore=tests/integration/")
            return [integration_cmd, non_integration_cmd]
        else:
            test_paths.append("tests/")
    else:
        if args.integration:
            test_paths.append("tests/integration/")
        if args.component:
            test_paths.append("tests/components/")
            cmd.append("--asyncio-mode=strict")  # Ensure asyncio strict mode for component tests
        if args.config:
            test_paths.append("tests/config/")
        if args.api:
            test_paths.append("tests/integration/test_api_endpoints.py")
        if args.file:
            test_paths.append(args.file)
        if args.test:
            if "/" in args.test or "." in args.test:
                # If it looks like a file path and test name
                test_paths.append(args.test)
            else:
                # If it's just a test name, try to find it
                test_paths.append(f"tests/integration/test_api_endpoints.py::test_{args.test}")
    
    # Add test paths to command
    cmd.extend(test_paths)
    
    # Add coverage if requested
    if args.coverage:
        cmd.insert(1, "-m")
        cmd.insert(2, "coverage")
        cmd.insert(3, "run")
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Disable output capture if requested
    if args.no_capture:
        cmd.append("-s")
    
    # Add asyncio debug mode if requested
    if args.event_loop_debug:
        cmd.append("--asyncio-mode=strict")
        os.environ["PYTHONASYNCIODEBUG"] = "1"
    else:
        # Always use strict mode to catch issues
        cmd.append("--asyncio-mode=strict")
    
    return [cmd]


def clean_test_cache():
    """Clean pytest cache directories."""
    print("Cleaning pytest cache...")
    subprocess.run(["rm", "-rf", ".pytest_cache"], check=False)
    
    # Also clear __pycache__ directories in tests
    for root, dirs, _ in os.walk("tests"):
        for d in dirs:
            if d == "__pycache__":
                cache_dir = os.path.join(root, d)
                print(f"Removing {cache_dir}")
                subprocess.run(["rm", "-rf", cache_dir], check=False)


def setup_isolated_env():
    """Set up an isolated environment for tests."""
    # Make sure we start with the right Python path
    os.environ["PYTHONPATH"] = os.path.abspath(".")
    
    # Clear any previous test-related environment variables
    for key in list(os.environ.keys()):
        if key.startswith(("PYTEST_", "MCP_TEST_")):
            del os.environ[key]
    
    # Set standard test variables
    os.environ["MCP_TEST_MODE"] = "1"
    os.environ["MCP_HOST"] = "localhost"
    os.environ["MCP_PORT"] = "8000"  # Different from default to avoid conflicts
    os.environ["QDRANT_URL"] = "http://localhost:6333"
    
    # Use unique collection names for tests to avoid interference
    test_id = os.urandom(4).hex()
    os.environ["MCP_COLLECTION_NAME"] = f"test_collection_{test_id}"
    
    # Configure asyncio behavior for better isolation
    os.environ["ASYNCIO_WATCHDOG_TIMEOUT"] = "30"
    os.environ["PYTEST_ASYNC_TEST_TIMEOUT"] = "60"
    
    # Force module isolation 
    os.environ["PYTEST_FORCE_ISOLATED_EVENT_LOOP"] = "1"


def run_tests(cmds: List[List[str]], env=None) -> int:
    """Run the tests with the given commands."""
    exit_code = 0
    
    for cmd in cmds:
        print(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, env=env)
            if result.returncode != 0:
                exit_code = result.returncode
        except Exception as e:
            print(f"Error running command: {e}")
            exit_code = 1
    
    return exit_code


def find_test_modules(directory="tests", filter_pattern=None):
    """Find all Python test files in the given directory."""
    test_modules = []
    
    # Walk through the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                module_path = os.path.join(root, file)
                
                # Apply filter if provided
                if filter_pattern and filter_pattern not in module_path:
                    continue
                    
                test_modules.append(module_path)
    
    return test_modules


def run_isolated_modules(args) -> int:
    """Run each test module in its own process for complete isolation."""
    # Determine which test modules to run
    test_modules = []
    
    if args.component:
        # For component tests, always run them individually
        test_modules = find_test_modules("tests/components")
    elif args.all:
        # When running all tests, get everything
        test_modules = find_test_modules()
    else:
        # Otherwise, run as specified
        if args.integration:
            integration_modules = find_test_modules("tests/integration")
            test_modules.extend(integration_modules)
        if args.config:
            config_modules = find_test_modules("tests/config")
            test_modules.extend(config_modules)
    
    # Sort modules to run in a specific order: regular tests first,
    # then component tests, and integration tests last
    def module_sort_key(module_path):
        if "integration" in module_path:
            return 3  # Run integration tests last
        elif "components" in module_path:
            return 2  # Run component tests in the middle
        else:
            return 1  # Run other tests first
    
    test_modules.sort(key=module_sort_key)
    
    # If specific test file was specified, only run that one
    if args.file:
        if os.path.exists(args.file):
            test_modules = [args.file]
        else:
            # Try to find the file in the tests directory
            matching_modules = [m for m in test_modules if args.file in m]
            if matching_modules:
                test_modules = matching_modules
            else:
                print(f"Error: Test file {args.file} not found")
                return 1
    
    final_exit_code = 0
    
    # Run each module in a separate process
    for module in test_modules:
        print(f"\n=== Running isolated test module: {module} ===\n")
        
        # Check if this is a component test
        is_component_test = "components" in module
        is_vector_store_test = "test_vector_store.py" in module
        is_knowledge_base_test = "test_knowledge_base.py" in module
        is_task_manager_test = "test_task_manager.py" in module
        
        # Prepare environment for this test module
        env = os.environ.copy()
        
        # Basic environment setup for all tests
        env["PYTEST_FORCE_ISOLATED_EVENT_LOOP"] = "1"
        env["MCP_TEST_MODE"] = "1"
        
        # Add special handling for component tests
        if is_component_test:
            # Ensure component tests run with asyncio strict mode
            env["PYTEST_ASYNCIO_MODE"] = "strict"
            
            # Component tests need test database config
            if "MCP_COLLECTION_NAME" not in env:
                env["MCP_COLLECTION_NAME"] = f"test_collection_{uuid.uuid4().hex[:8]}"
            
            # Vector store and knowledge base tests need additional time for setup
            if is_vector_store_test or is_knowledge_base_test or is_task_manager_test:
                env["PYTEST_TIMEOUT"] = "60"  # Allow more time for these tests
        
        # For component tests, use our specialized component test runner
        if is_component_test and args.fully_isolated:
            print(f"Using specialized component test runner for {module}")
            # Extract test names from the module using a simple pattern match
            component_test_results = []
            try:
                # Use grep to find test functions in the file - more reliable
                # than pytest --collect-only in this case
                grep_cmd = ["grep", "-E", "^def test_", module]
                result = subprocess.run(grep_cmd, capture_output=True, text=True)
                collected_test_names = []
                
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        # Extract the test name from "def test_name(...)"
                        if line.startswith("def test_"):
                            test_name = line.split("def ")[1].split("(")[0].strip()
                            collected_test_names.append(test_name)
                    print(f"Found {len(collected_test_names)} tests in {module}")
                else:
                    # Fall back to read the file directly
                    with open(module, 'r') as f:
                        content = f.read()
                        # Use a simple regex to find all test functions
                        import re
                        matches = re.findall(r'def\s+(test_\w+)\s*\(', content)
                        collected_test_names = matches
                        print(f"Found {len(collected_test_names)} tests in {module} (using file read)")
            except Exception as e:
                print(f"Error extracting tests from {module}: {e}")
                # Just skip this module and continue with others
                continue
                
            # Run each test separately using our component test runner
            if collected_test_names:
                for test_name in collected_test_names:
                    print(f"Running test: {module}::{test_name}")
                    
                    # Use our specialized component test runner
                    runner_cmd = [
                        "python", 
                        "component_test_runner.py", 
                        module, 
                        test_name
                    ]
                    
                    print(f"Running: {' '.join(runner_cmd)}")
                    test_result = subprocess.run(runner_cmd, env=env)
                    component_test_results.append((test_name, test_result.returncode))
                    
                    # If we have a failure, record it but continue running other tests
                    if test_result.returncode != 0:
                        final_exit_code = test_result.returncode
                    
                    # Short pause between tests to let resources clean up
                    time.sleep(1.0)
                
                # Print summary of test results for this module
                print(f"\n=== Test Results for {module} ===")
                passed = sum(1 for _, code in component_test_results if code == 0)
                failed = sum(1 for _, code in component_test_results if code != 0)
                print(f"Passed: {passed}, Failed: {failed}, Total: {len(component_test_results)}")
                for name, code in component_test_results:
                    status = "PASSED" if code == 0 else "FAILED"
                    print(f"{name}: {status}")
                print("=" * 40)
            else:
                print(f"No tests found in {module}, skipping")
        else:
            # For other tests, use our standard command builder
            cmd_args = argparse.Namespace(**vars(args))
            cmds = build_command(cmd_args, module)
            
            # Run this module's tests with the prepared environment
            module_result = run_tests(cmds, env)
            
            # If we have a failure, record it but continue running other modules
            if module_result != 0:
                final_exit_code = module_result
        
        # Short pause between modules to let event loops clean up
        # Increase delay for component tests with complex cleanup needs
        if is_component_test:
            time.sleep(1.5)  # Longer pause for component tests
        else:
            time.sleep(0.5)
    
    return final_exit_code


def run_component_tests_fully_isolated(test_file=None):
    """Run component tests with each test completely isolated using specialized runner."""
    print("\n=== Running component tests in fully isolated mode ===\n")

    # Find component test files
    if test_file:
        test_files = [test_file]
    else:
        test_files = find_test_modules("tests/components")
    
    overall_results = {}
    
    for test_file in test_files:
        print(f"\n=== Running isolated test module: {test_file} ===\n")
        print(f"Using specialized component test runner for {test_file}")
        
        try:
            # Use the component_test_runner's discovery mechanism
            from component_test_runner import get_module_tests
            tests = get_module_tests(test_file)
            print(f"Found {len(tests)} tests in {test_file} (using file read)")
            
            # Skip if no tests found
            if not tests:
                print(f"No tests found in {test_file}")
                continue
            
            # Track results
            passed_tests = []
            failed_tests = []
            
            for test_name in tests:
                print(f"Running test: {test_file}::{test_name}")
                cmd = f"python component_test_runner.py {test_file} {test_name}"
                print(f"Running: {cmd}")
                
                result = subprocess.run(cmd, shell=True)
                
                if result.returncode == 0:
                    passed_tests.append(test_name)
                else:
                    failed_tests.append(test_name)
            
            # Report results for this file
            print(f"\n=== Test Results for {test_file} ===")
            print(f"Passed: {len(passed_tests)}, Failed: {len(failed_tests)}, Total: {len(tests)}")
            
            for test in tests:
                status = "PASSED" if test in passed_tests else "FAILED"
                print(f"{test}: {status}")
            
            print("========================================")
            
            # Store results
            overall_results[test_file] = {
                "passed": len(passed_tests),
                "failed": len(failed_tests),
                "total": len(tests)
            }
        except Exception as e:
            print(f"Error running tests for {test_file}: {e}")
            traceback.print_exc()
            overall_results[test_file] = {
                "passed": 0,
                "failed": 1,
                "total": 1,
                "error": str(e)
            }
    
    # Determine if any tests failed
    any_failures = any(result.get("failed", 0) > 0 for result in overall_results.values())
    return 1 if any_failures else 0


def generate_coverage_report(html: bool = False) -> Optional[int]:
    """Generate coverage report."""
    if html:
        cmd = ["python", "-m", "coverage", "html"]
        print("Generating HTML coverage report...")
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"HTML coverage report generated in {os.path.abspath('htmlcov')}")
        return result.returncode
    else:
        cmd = ["python", "-m", "coverage", "report", "--show-missing"]
        print("Generating coverage report...")
        return subprocess.run(cmd).returncode


def run_all_tests(args):
    """Run all tests."""
    cmds = build_command(args)
    print(f"Running: {' '.join(cmds[0])}")
    exit_code = 0
    
    # For regular test runs or when not in fully isolated mode, 
    # first attempt to run everything as a single command
    if args.sequential:
        # Run all tests sequentially
        exit_code = run_tests(cmds)
    else:
        try:
            # First, try to run all tests as one command
            exit_code = run_tests(cmds, os.environ.copy())
        except Exception as e:
            print(f"Error running tests: {e}")
            exit_code = 1
        
        # If test failed or not all modules were specified, run each module individually
        if exit_code != 0 or args.fully_isolated:
            print("\nRunning tests with full module isolation...")
            exit_code = run_isolated_modules(args)
    
    return exit_code


def main():
    """Main entry point."""
    args = parse_args()
    
    # Clean test cache if requested
    if args.clean:
        clean_test_cache()
    
    # Setup isolated environment if requested
    if args.isolated or args.fully_isolated:
        setup_isolated_env()
    
    # Set up environment variables
    if args.component:
        os.environ["MCP_TEST_MODE"] = "1"
        # Generate a unique collection name for isolated tests
        if args.isolated or args.fully_isolated:
            # Use a unique collection for each test run to ensure isolation
            unique_id = uuid.uuid4().hex[:8]
            os.environ["MCP_COLLECTION_NAME"] = f"test_collection_{unique_id}"
    
    # We need to set this for all async tests to ensure proper event loop handling
    if args.component or args.integration:
        os.environ["PYTEST_FORCE_ISOLATED_EVENT_LOOP"] = "1"
    
    # Print environment info
    if args.verbose:
        print("\nTest environment:")
        print(f"Python: {sys.executable}")
        if args.isolated or args.fully_isolated:
            print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
            print(f"Collection name: {os.environ.get('MCP_COLLECTION_NAME', 'Not set')}")
            print(f"Asyncio mode: strict")
    
    # We have special handling for component tests in fully-isolated mode
    if args.component and args.fully_isolated:
        # Skip general pytest run and go straight to component test runner
        exit_code = run_component_tests_fully_isolated(args.file)
        sys.exit(exit_code)
    
    # Regular test flow - first try to run all together
    exit_code = run_all_tests(args)
    
    # If not in isolated mode, we're done
    if not args.isolated and not args.component:
        # Generate coverage report if needed
        if args.coverage:
            generate_coverage_report(args.html)
        sys.exit(exit_code)
    
    # If tests failed and we're in isolated mode, run each file separately
    if exit_code != 0 and (args.isolated or args.component):
        isolated_exit_code = run_isolated_modules(args)
        
        # Generate coverage report if needed
        if args.coverage:
            generate_coverage_report(args.html)
        
        sys.exit(isolated_exit_code)
    
    # Generate coverage report if needed
    if args.coverage:
        generate_coverage_report(args.html)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()