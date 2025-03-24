"""Test fixtures for the codebase insight server."""

import asyncio
import logging
import os
import sys
import threading
import uuid
import warnings
from contextlib import ExitStack
from pathlib import Path
from threading import Lock
from typing import AsyncGenerator, Dict, Generator, Optional, Set

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.server import CodebaseAnalysisServer
from mcp_codebase_insight.server_test_isolation import get_isolated_server_state

logger = logging.getLogger(__name__)

# Track process-specific event loops with mutex protection
_event_loops: Dict[int, asyncio.AbstractEventLoop] = {}
_loops_lock = Lock()
_active_test_ids: Set[str] = set()
_tests_lock = Lock()

# Configure logging for better debug info
logging.basicConfig(level=logging.INFO)
asyncio_logger = logging.getLogger("asyncio")
asyncio_logger.setLevel(logging.INFO)

def _get_test_id():
    """Get a unique identifier for the current test."""
    return f"{os.getpid()}_{threading.get_ident()}"

# Primary event loop with session scope for compatibility with pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for the test session."""
    pid = os.getpid()
    logger.info(f"Creating session-scoped event loop for process {pid}")
    
    # Create and set a new loop for this session
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Store in our registry
    with _loops_lock:
        _event_loops[pid] = loop
    
    # Configure loop
    loop.set_debug(True)
    os.environ["ASYNCIO_WATCHDOG_TIMEOUT"] = "30"
    
    try:
        yield loop
    finally:
        # Make sure we clean up properly
        with _loops_lock:
            if pid in _event_loops:
                try:
                    logger.info(f"Cleaning up session event loop for process {pid}")
                    
                    # Cancel all tasks
                    tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]
                    if tasks:
                        logger.info(f"Cancelling {len(tasks)} pending tasks")
                        for task in tasks:
                            task.cancel()
                        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
                    
                    # Shut down async generators
                    loop.run_until_complete(loop.shutdown_asyncgens())
                    
                    # Close the loop
                    if not loop.is_closed():
                        loop.close()
                        logger.info(f"Event loop closed for process {pid}")
                    
                    # Clean up tracking
                    del _event_loops[pid]
                except Exception as e:
                    logger.error(f"Error during event loop cleanup: {e}")

# Function-scoped event loop for tests that need isolation
@pytest.fixture
def function_event_loop():
    """Create a function-scoped event loop for test isolation."""
    test_id = _get_test_id()
    logger.info(f"Creating function-scoped event loop for test {test_id}")
    
    # Create a new loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Configure loop
    loop.set_debug(True)
    
    with _tests_lock:
        _active_test_ids.add(test_id)
    
    try:
        yield loop
    finally:
        with _tests_lock:
            if test_id in _active_test_ids:
                _active_test_ids.remove(test_id)
        
        # Clean up
        try:
            # Cancel all tasks
            tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]
            if tasks:
                loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            
            # Shut down async generators
            loop.run_until_complete(loop.shutdown_asyncgens())
            
            # Close the loop
            loop.close()
        except Exception as e:
            logger.error(f"Error during function event loop cleanup: {e}")

@pytest.fixture(scope="session")
def anyio_backend():
    """Configure pytest-asyncio to use asyncio backend."""
    return "asyncio"

@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_server_config():
    """Create a server configuration for tests."""
    config = ServerConfig(
        host="localhost",
        port=8000,
        log_level="DEBUG",
        qdrant_url="http://localhost:6333",
        docs_cache_dir=Path(".test_cache") / "docs",
        adr_dir=Path(".test_cache") / "docs/adrs",
        kb_storage_dir=Path(".test_cache") / "knowledge",
        embedding_model="all-MiniLM-L6-v2",
        collection_name=f"test_collection_{uuid.uuid4().hex[:8]}",
        debug_mode=True,
        metrics_enabled=False,
        cache_enabled=True,
        memory_cache_size=1000,
        disk_cache_dir=Path(".test_cache") / "cache"
    )
    return config

# Session-scoped server instance for shared resources
@pytest_asyncio.fixture(scope="session")
async def session_test_server(event_loop, test_server_config):
    """Create a session-scoped server instance for shared tests."""
    logger.info(f"Creating session-scoped test server instance")
    
    # Create server with isolated state
    server = CodebaseAnalysisServer(test_server_config)
    instance_id = f"test_server_{uuid.uuid4().hex}"
    server.state = get_isolated_server_state(instance_id)
    
    try:
        # Initialize state
        if not server.state.initialized:
            logger.info("Initializing server state...")
            await server.state.initialize()
            logger.info("Server state initialized successfully")
        
        # Initialize server
        if not server.is_initialized:
            logger.info("Initializing server...")
            await server.initialize()
            logger.info("Server initialized successfully")
        
        yield server
    finally:
        try:
            # Clean up server state
            logger.info("Starting server cleanup...")
            
            # Check server.state exists and is initialized
            if hasattr(server, 'state') and server.state and hasattr(server.state, 'initialized') and server.state.initialized:
                logger.info("Cleaning up server state...")
                try:
                    await server.state.cleanup()
                    logger.info("Server state cleanup completed")
                except Exception as e:
                    logger.error(f"Error during server state cleanup: {e}")
            
            # Check server is initialized
            if hasattr(server, 'is_initialized') and server.is_initialized:
                logger.info("Shutting down server...")
                try:
                    await server.shutdown()
                    logger.info("Server shutdown completed")
                except Exception as e:
                    logger.error(f"Error during server shutdown: {e}")
        except Exception as e:
            logger.error(f"Error during overall server cleanup: {e}")

# Function-scoped server instance for isolated tests
@pytest_asyncio.fixture
async def test_server_instance(function_event_loop, test_server_config):
    """Create a function-scoped server instance for isolated tests."""
    logger.info(f"Creating function-scoped test server instance for test {_get_test_id()}")
    
    # Create server with isolated state
    server = CodebaseAnalysisServer(test_server_config)
    instance_id = f"test_server_{uuid.uuid4().hex}"
    server.state = get_isolated_server_state(instance_id)
    
    try:
        # Initialize state
        if not server.state.initialized:
            logger.info("Initializing server state...")
            await server.state.initialize()
            logger.info("Server state initialized successfully")
        
        # Initialize server
        if not server.is_initialized:
            logger.info("Initializing server...")
            await server.initialize()
            logger.info("Server initialized successfully")
        
        yield server
    finally:
        try:
            # Clean up server state
            logger.info("Starting server cleanup...")
            
            # Check server.state exists and is initialized
            if hasattr(server, 'state') and server.state and hasattr(server.state, 'initialized') and server.state.initialized:
                logger.info("Cleaning up server state...")
                try:
                    await server.state.cleanup()
                    logger.info("Server state cleanup completed")
                except Exception as e:
                    logger.error(f"Error during server state cleanup: {e}")
            
            # Check server is initialized
            if hasattr(server, 'is_initialized') and server.is_initialized:
                logger.info("Shutting down server...")
                try:
                    await server.shutdown()
                    logger.info("Server shutdown completed")
                except Exception as e:
                    logger.error(f"Error during server shutdown: {e}")
        except Exception as e:
            logger.error(f"Error during overall server cleanup: {e}")

# Session-scoped httpx client
@pytest_asyncio.fixture(scope="session")
async def session_httpx_client(session_test_server):
    """Create a session-scoped httpx client for shared tests."""
    logger.info(f"Creating session-scoped httpx test client")
    
    # Configure transport with proper ASGI handling
    transport = httpx.ASGITransport(
        app=session_test_server.app,
        raise_app_exceptions=False,
    )
    
    # Create client
    client = httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=True,
        timeout=30.0
    )
    
    logger.info("Session-scoped httpx test client created")
    
    try:
        yield client
    finally:
        try:
            await client.aclose()
            logger.info("Session-scoped httpx test client closed")
        except Exception as e:
            logger.error(f"Error during session client cleanup: {e}")

# Function-scoped httpx client
@pytest_asyncio.fixture
async def httpx_test_client(test_server_instance):
    """Create a function-scoped httpx client for isolated tests."""
    logger.info(f"Creating function-scoped httpx test client for test {_get_test_id()}")
    
    # Configure transport with proper ASGI handling
    transport = httpx.ASGITransport(
        app=test_server_instance.app,
        raise_app_exceptions=False,
    )
    
    # Create client
    client = httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=True,
        timeout=30.0
    )
    
    logger.info("Function-scoped httpx test client created")
    
    try:
        yield client
    finally:
        try:
            await client.aclose()
            logger.info("Function-scoped httpx test client closed")
        except Exception as e:
            logger.error(f"Error during client cleanup: {e}")

# Default client for tests (currently using session-scoped client)
@pytest_asyncio.fixture
async def client(session_httpx_client) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Return the current httpx test client.
    
    This is a function-scoped async fixture that yields the session-scoped client.
    Tests can override this to use the function-scoped client if needed.
    """
    yield session_httpx_client

# Test data fixtures
@pytest.fixture
def test_code():
    """Provide sample code for tests."""
    return """
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n-1)
    """

@pytest.fixture
def test_issue():
    """Provide a sample issue for tests."""
    return {
        "title": "Test Issue",
        "description": "This is a test issue for debugging",
        "code": "print('hello world')",
        "error": "TypeError: unsupported operand type(s)",
    }

@pytest.fixture
def test_adr():
    """Provide a sample ADR for tests."""
    return {
        "title": "Test ADR",
        "status": "proposed",
        "context": "This is a test ADR for testing",
        "decision": "We decided to test the ADR system",
        "consequences": "Testing will be successful",
    }

# Define custom pytest hooks
def pytest_configure(config):
    """Configure pytest with our specific settings."""
    config.addinivalue_line(
        "markers", "isolated_event_loop: mark test to use an isolated event loop"
    )
    
    # Suppress event loop warnings
    warnings.filterwarnings(
        "ignore", 
        message="There is no current event loop",
        category=DeprecationWarning
    )
    warnings.filterwarnings(
        "ignore", 
        message="The loop argument is deprecated",
        category=DeprecationWarning
    )

def pytest_runtest_setup(item):
    """Set up for each test."""
    # Get the module name for the test
    module_name = item.module.__name__ if hasattr(item, 'module') else ''
    
    # Set an environment variable with the current test module
    # This helps with test isolation in the server code
    os.environ['CURRENT_TEST_MODULE'] = module_name
    os.environ['CURRENT_TEST_NAME'] = item.name if hasattr(item, 'name') else ''
    
    # For any async test, ensure we have a valid event loop
    if 'asyncio' in item.keywords:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                logger.warning(f"Found closed loop in {module_name}:{item.name}, creating new loop")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            logger.warning(f"No event loop found in {module_name}:{item.name}, creating new loop")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

def pytest_runtest_teardown(item):
    """Clean up after each test."""
    # Clear the current test environment variables
    if 'CURRENT_TEST_MODULE' in os.environ:
        del os.environ['CURRENT_TEST_MODULE']
    if 'CURRENT_TEST_NAME' in os.environ:
        del os.environ['CURRENT_TEST_NAME']

# Cleanup fixture
@pytest.fixture(autouse=True, scope="session")
def cleanup_server_states(event_loop: asyncio.AbstractEventLoop):
    """Clean up any lingering server states."""
    from mcp_codebase_insight.server_test_isolation import _server_states
    
    yield
    
    try:
        # Report any unclosed instances
        logger.info(f"Found {len(_server_states)} server states at end of session")
        for instance_id, state in list(_server_states.items()):
            logger.info(f"Cleaning up state for instance: {instance_id}")
            try:
                if state.initialized:
                    try:
                        # Use the event loop for cleanup
                        if not event_loop.is_closed():
                            event_loop.run_until_complete(state.cleanup())
                    except Exception as e:
                        logger.error(f"Error cleaning up state: {e}")
            except Exception as e:
                logger.error(f"Error checking state initialized: {e}")
    except Exception as e:
        logger.error(f"Error during server states cleanup: {e}")
    
    try:
        # Cancel any remaining tasks
        for pid, loop in list(_event_loops.items()):
            if not loop.is_closed():
                for task in asyncio.all_tasks(loop):
                    if not task.done() and not task.cancelled():
                        logger.warning(f"Force cancelling task: {task.get_name()}")
                        task.cancel()
    except Exception as e:
        logger.error(f"Error cancelling tasks: {e}")

# Custom test marker for isolated event loops
def pytest_collection_modifyitems(items):
    """Add the isolated_event_loop marker to integration tests."""
    for item in items:
        module_name = item.module.__name__ if hasattr(item, 'module') else ''
        if 'integration' in module_name:
            # Add our custom marker to all integration tests
            item.add_marker(pytest.mark.isolated_event_loop)
