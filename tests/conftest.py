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

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.mcp_codebase_insight.core.config import ServerConfig
from src.mcp_codebase_insight.server import CodebaseAnalysisServer
from src.mcp_codebase_insight.server_test_isolation import get_isolated_server_state

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
    
    with _loops_lock:
        _event_loops[pid] = loop
        
    yield loop
    
    # Final cleanup
    with _loops_lock:
        if pid in _event_loops:
            del _event_loops[pid]
    
    # Close the loop to prevent asyncio related warnings
    try:
        if not loop.is_closed():
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
    except:
        logger.exception("Error closing session event loop")

# To address the event_loop fixture scope mismatch issue, we'll use a different approach
# We'll have a single session-scoped event loop that's accessible to function-scoped fixtures
@pytest.fixture(scope="function")
def function_event_loop(event_loop):
    """
    Create a function-scoped event loop proxy for test isolation.
    
    This approach avoids the ScopeMismatch error by using the session-scoped event_loop 
    but providing function-level isolation.
    """
    # Return the session loop, but track the test in our isolation system
    test_id = _get_test_id()
    logger.debug(f"Using function-level event loop isolation for test {test_id}")
    
    with _tests_lock:
        _active_test_ids.add(test_id)
    
    yield event_loop
    
    with _tests_lock:
        if test_id in _active_test_ids:
            _active_test_ids.remove(test_id)

@pytest.fixture(scope="session")
def anyio_backend():
    """Configure pytest-asyncio to use asyncio backend."""
    return "asyncio"

@pytest.fixture(scope="session")
def test_server_config():
    """Create a server configuration for tests."""
    # For CI/CD environment, use the environment variables if available
    qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    
    # Use the CI/CD collection name if provided, otherwise generate a unique one
    collection_name = os.environ.get("COLLECTION_NAME", f"test_collection_{uuid.uuid4().hex[:8]}")
    
    # Optional: Use a shorter embedding model for tests to save resources
    embedding_model = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    logger.info(f"Configuring test server with Qdrant URL: {qdrant_url}, collection: {collection_name}")
    
    config = ServerConfig(
        host="localhost",
        port=8000,
        log_level="DEBUG",
        qdrant_url=qdrant_url,
        docs_cache_dir=Path(".test_cache") / "docs",
        adr_dir=Path(".test_cache") / "docs/adrs",
        kb_storage_dir=Path(".test_cache") / "knowledge",
        embedding_model=embedding_model,
        collection_name=collection_name,
        debug_mode=True,
        metrics_enabled=False,
        cache_enabled=True,
        memory_cache_size=1000,
        disk_cache_dir=Path(".test_cache") / "cache"
    )
    return config

# Make the qdrant_client fixture session-scoped to avoid connection issues
@pytest.fixture(scope="session")
def qdrant_client(test_server_config):
    """Create a shared Qdrant client for tests."""
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    
    # Connect to Qdrant
    client = QdrantClient(url=test_server_config.qdrant_url)
    
    # Create the collection if it doesn't exist
    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        # If collection doesn't exist, create it
        if test_server_config.collection_name not in collection_names:
            logger.info(f"Creating test collection: {test_server_config.collection_name}")
            client.create_collection(
                collection_name=test_server_config.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Dimension for all-MiniLM-L6-v2
                    distance=models.Distance.COSINE,
                ),
            )
        else:
            logger.info(f"Collection {test_server_config.collection_name} already exists")
    except Exception as e:
        logger.warning(f"Error checking/creating Qdrant collection: {e}")
    
    yield client
    
    # Cleanup - delete the collection at the end of the session
    try:
        if test_server_config.collection_name.startswith("test_"):
            logger.info(f"Cleaning up test collection: {test_server_config.collection_name}")
            client.delete_collection(collection_name=test_server_config.collection_name)
    except Exception as e:
        logger.warning(f"Error deleting Qdrant collection: {e}")

# Session-scoped server instance for shared resources
@pytest_asyncio.fixture(scope="session")
async def session_test_server(event_loop, test_server_config):
    """Create a session-scoped server instance for shared tests."""
    logger.info(f"Creating session-scoped test server instance")
    
    # Create the server instance with the provided test configuration
    server = CodebaseAnalysisServer(test_server_config)
    
    # Initialize the server state
    logger.info("Initializing server state...")
    await server.state.initialize()
    logger.info("Server state initialized successfully")
    
    # Initialize the server
    logger.info("Initializing server...")
    await server.initialize()
    logger.info("Server initialized successfully")
    
    # Create and mount MCP server
    from src.mcp_codebase_insight.core.sse import MCP_CodebaseInsightServer, create_sse_server
    from src.mcp_codebase_insight.core.state import ComponentStatus
    
    logger.info("Creating and mounting MCP server...")
    try:
        # Create SSE server
        sse_server = create_sse_server()
        logger.info("Created SSE server")
        
        # Mount SSE server
        server.app.mount("/mcp", sse_server)
        logger.info("Mounted SSE server at /mcp")
        
        # Create MCP server instance
        mcp_server = MCP_CodebaseInsightServer(server.state)
        logger.info("Created MCP server instance")
        
        # Register tools
        mcp_server.register_tools()
        logger.info("Registered MCP server tools")
        
        # Update component status
        server.state.update_component_status(
            "mcp_server",
            ComponentStatus.INITIALIZED,
            instance=mcp_server
        )
        logger.info("Updated MCP server component status")
        
    except Exception as e:
        logger.error(f"Failed to create/mount MCP server: {e}", exc_info=True)
        raise RuntimeError(f"Failed to create/mount MCP server: {e}")
    
    # Add test-specific endpoints
    @server.app.get("/direct-sse")
    async def direct_sse_endpoint():
        """Test endpoint for direct SSE connection."""
        from starlette.responses import Response
        return Response(
            content="data: Direct SSE test endpoint\n\n",
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    @server.app.get("/mcp/sse-mock")
    async def mock_sse_endpoint():
        """Mock SSE endpoint for testing."""
        from starlette.responses import Response
        return Response(
            content="data: Mock SSE endpoint\n\n",
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    @server.app.get("/debug/routes")
    async def debug_routes():
        """Debug endpoint to list all registered routes."""
        from starlette.responses import Response
        routes = []
        for route in server.app.routes:
            route_info = {
                "path": getattr(route, "path", str(route)),
                "methods": getattr(route, "methods", set()),
                "name": getattr(route, "name", None),
                "endpoint": str(getattr(route, "endpoint", None))
            }
            routes.append(route_info)
        return {"routes": routes}
    
    @server.app.get("/health")
    async def health_check_test():
        """Health check endpoint for testing."""
        mcp_server = server.state.get_component("mcp_server")
        return {
            "status": "ok",
            "initialized": server.state.initialized,
            "mcp_available": mcp_server is not None,
            "instance_id": server.state.instance_id,
            "components": server.state.list_components()
        }
    
    # Start the server
    logger.info("Starting test server...")
    await server.start()
    logger.info("Test server started successfully")
    
    yield server
    
    # Cleanup
    logger.info("Cleaning up test server...")
    await server.stop()
    logger.info("Test server cleanup complete")

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
def pytest_collection_modifyitems(items):
    """Add the isolated_event_loop marker to integration tests."""
    for item in items:
        module_name = item.module.__name__ if hasattr(item, 'module') else ''
        if 'integration' in module_name:
            # Add our custom marker to all integration tests
            item.add_marker(pytest.mark.isolated_event_loop)

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
    from src.mcp_codebase_insight.server_test_isolation import _server_states
    
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
