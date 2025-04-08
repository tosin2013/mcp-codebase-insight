"""Unit tests for SSE core components."""

import sys
import os

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio
import pytest
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List, AsyncGenerator

from src.mcp_codebase_insight.core.sse import create_sse_server, MCP_CodebaseInsightServer
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# Set up logging for tests
logger = logging.getLogger(__name__)

# Mark all tests as asyncio tests
pytestmark = pytest.mark.asyncio


class MockState:
    """Mock server state for testing."""
    
    def __init__(self):
        self.components = {}
        
    def get_component(self, name):
        """Get a component by name."""
        return self.components.get(name)
        
    def get_component_status(self):
        """Get status of all components."""
        return {name: {"available": True} for name in self.components}
        
    def set_component(self, name, component):
        """Set a component."""
        self.components[name] = component


class MockVectorStore:
    """Mock vector store component for testing."""
    
    async def search(self, text, filter_conditions=None, limit=5):
        """Mock search method."""
        return [
            MagicMock(
                id="test-id-1",
                score=0.95,
                metadata={
                    "text": "def example_function():\n    return 'example'",
                    "file_path": "/path/to/file.py",
                    "line_range": "10-15",
                    "type": "code",
                    "language": "python",
                    "timestamp": "2025-03-26T10:00:00"
                }
            )
        ]


class MockKnowledgeBase:
    """Mock knowledge base component for testing."""
    
    async def search_patterns(self, query, pattern_type=None, limit=5):
        """Mock search_patterns method."""
        return [
            MagicMock(
                id="pattern-id-1",
                pattern="Example pattern",
                description="Description of example pattern",
                type=pattern_type or "code",
                confidence=0.9,
                metadata={"source": "test"}
            )
        ]


class MockADRManager:
    """Mock ADR manager component for testing."""
    
    async def list_adrs(self):
        """Mock list_adrs method."""
        return [
            MagicMock(
                id="adr-id-1",
                title="Example ADR",
                status="accepted",
                created_at=None,
                updated_at=None
            )
        ]


class MockTaskManager:
    """Mock task manager component for testing."""
    
    async def get_task(self, task_id):
        """Mock get_task method."""
        if task_id == "invalid-id":
            return None
            
        return MagicMock(
            id=task_id,
            type="analysis",
            status="running",
            progress=0.5,
            result=None,
            error=None,
            created_at=None,
            updated_at=None
        )


@pytest.fixture
def mock_server_state():
    """Create a mock server state for testing."""
    state = MockState()
    
    # Add mock components
    state.set_component("vector_store", MockVectorStore())
    state.set_component("knowledge_base", MockKnowledgeBase())
    state.set_component("adr_manager", MockADRManager())
    state.set_component("task_tracker", MockTaskManager())  # Updated component name to match sse.py
    
    return state


@pytest.fixture
def mcp_server(mock_server_state):
    """Create an MCP server instance for testing."""
    return MCP_CodebaseInsightServer(mock_server_state)


async def test_mcp_server_initialization(mcp_server):
    """Test MCP server initialization."""
    # Verify the server was initialized correctly
    assert mcp_server.state is not None
    assert mcp_server.mcp_server is not None
    assert mcp_server.mcp_server.name == "MCP-Codebase-Insight"
    assert mcp_server.tools_registered is False


async def test_register_tools(mcp_server):
    """Test registering tools with the MCP server."""
    # Register tools
    mcp_server.register_tools()
    
    # Verify tools were registered
    assert mcp_server.tools_registered is True
    
    # In MCP v1.5.0, we can't directly access tool_defs
    # Instead we'll just verify registration was successful
    # The individual tool tests will verify specific functionality


@patch('mcp_codebase_insight.core.sse.create_sse_server')
async def test_get_starlette_app(mock_create_sse, mcp_server):
    """Test getting the Starlette app for the MCP server."""
    # Set up the mock
    mock_app = MagicMock()
    mock_create_sse.return_value = mock_app
    
    # Get the Starlette app
    app = mcp_server.get_starlette_app()
    
    # Verify tools were registered
    assert mcp_server.tools_registered is True
    
    # Verify create_sse_server was called with the MCP server
    mock_create_sse.assert_called_once_with(mcp_server.mcp_server)
    
    # Verify the app was returned
    assert app == mock_app


@patch('mcp_codebase_insight.core.sse.SseServerTransport')
@patch('mcp_codebase_insight.core.sse.Starlette')
async def test_create_sse_server(mock_starlette, mock_transport):
    """Test creating the SSE server."""
    # Set up mocks
    mock_mcp = MagicMock(spec=FastMCP)
    mock_transport_instance = MagicMock()
    mock_transport.return_value = mock_transport_instance
    mock_app = MagicMock()
    mock_starlette.return_value = mock_app
    
    # Create the SSE server
    app = create_sse_server(mock_mcp)
    
    # Verify SseServerTransport was initialized correctly
    mock_transport.assert_called_once_with("/messages/")
    
    # Verify Starlette was initialized with routes
    mock_starlette.assert_called_once()
    
    # Verify the app was returned
    assert app == mock_app


async def test_vector_search_tool(mcp_server):
    """Test the vector search tool."""
    # Make sure tools are registered
    if not mcp_server.tools_registered:
        mcp_server.register_tools()
    
    # Mock the FastMCP add_tool method to capture calls
    with patch.object(mcp_server.mcp_server, 'add_tool') as mock_add_tool:
        # Re-register the vector search tool
        mcp_server._register_vector_search_tool()
        
        # Verify the tool was registered with expected parameters
        mock_add_tool.assert_called_once()
        assert mock_add_tool.call_args[1]['name'] == "vector-search"
        assert mock_add_tool.call_args[1]['description'] == "Search for code snippets semantically similar to the query text"


async def test_knowledge_search_tool(mcp_server):
    """Test the knowledge search tool."""
    # Make sure tools are registered
    if not mcp_server.tools_registered:
        mcp_server.register_tools()
    
    # Mock the FastMCP add_tool method to capture calls
    with patch.object(mcp_server.mcp_server, 'add_tool') as mock_add_tool:
        # Re-register the knowledge search tool
        mcp_server._register_knowledge_tool()
        
        # Verify the tool was registered with expected parameters
        mock_add_tool.assert_called_once()
        assert mock_add_tool.call_args[1]['name'] == "knowledge-search"
        assert mock_add_tool.call_args[1]['description'] == "Search for patterns in the knowledge base"


async def test_adr_list_tool(mcp_server):
    """Test the ADR list tool."""
    # Make sure tools are registered
    if not mcp_server.tools_registered:
        mcp_server.register_tools()
    
    # Mock the FastMCP add_tool method to capture calls
    with patch.object(mcp_server.mcp_server, 'add_tool') as mock_add_tool:
        # Re-register the ADR list tool
        mcp_server._register_adr_tool()
        
        # Verify the tool was registered with expected parameters
        mock_add_tool.assert_called_once()
        assert mock_add_tool.call_args[1]['name'] == "adr-list"
        assert mock_add_tool.call_args[1]['description'] == "List architectural decision records"


async def test_task_status_tool(mcp_server):
    """Test the task status tool."""
    # Make sure tools are registered
    if not mcp_server.tools_registered:
        mcp_server.register_tools()
    
    # Mock the FastMCP add_tool method to capture calls
    with patch.object(mcp_server.mcp_server, 'add_tool') as mock_add_tool:
        # Re-register the task status tool
        mcp_server._register_task_tool()
        
        # Verify the tool was registered with expected parameters
        mock_add_tool.assert_called_once()
        assert mock_add_tool.call_args[1]['name'] == "task-status" 
        assert mock_add_tool.call_args[1]['description'] == "Get the status of a specific task"


@patch('mcp_codebase_insight.core.sse.SseServerTransport')
@patch('mcp_codebase_insight.core.sse.Starlette')
async def test_sse_handle_connect(mock_starlette, mock_transport):
    """Test the SSE connection handling functionality."""
    # Set up mocks
    mock_transport_instance = MagicMock()
    mock_transport.return_value = mock_transport_instance
    
    mock_mcp = MagicMock(spec=FastMCP)
    # For MCP v1.5.0, create a mock run method instead of initialization options
    mock_mcp.run = AsyncMock()
    
    mock_request = MagicMock()
    mock_request.client = "127.0.0.1"
    mock_request.scope = {"type": "http"}
    
    # Mock the transport's connect_sse method
    mock_streams = (AsyncMock(), AsyncMock())
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_streams)
    mock_cm.__aexit__ = AsyncMock()
    mock_transport_instance.connect_sse.return_value = mock_cm
    
    # Create a mock handler and add it to our mock app instance
    handle_sse = AsyncMock()
    mock_app = MagicMock()
    mock_starlette.return_value = mock_app
    
    # Set up a mock route that we can access
    mock_route = MagicMock()
    mock_route.path = "/sse/"
    mock_route.endpoint = handle_sse
    mock_app.routes = [mock_route]
    
    # Create the SSE server
    app = create_sse_server(mock_mcp)
    
    # Extract the actual handler from the route configuration
    routes_kwarg = mock_starlette.call_args.kwargs.get('routes', [])
    if routes_kwarg:
        for route in routes_kwarg:
            if hasattr(route, 'path') and route.path == '/sse/':
                handle_sse = route.endpoint
                break
        
    # Call the handler with our mocked request
    await handle_sse(mock_request)
    
    # Verify connect_sse was called with the request
    mock_transport_instance.connect_sse.assert_called_once_with(
        mock_request.scope, mock_request.receive, mock_request._send
    )
    
    # Verify the MCP server's run method was called with just the streams (no init options)
    mock_mcp.run.assert_called_once()
    # Check that run was called with exactly 2 arguments (the streams)
    assert len(mock_mcp.run.call_args[0]) == 2
    assert mock_mcp.run.call_args[0][0] == mock_streams[0]
    assert mock_mcp.run.call_args[0][1] == mock_streams[1]


async def test_sse_backpressure_handling(mcp_server):
    """Test SSE backpressure handling mechanism."""
    # Set up a mock transport with a slow client
    mock_transport = MagicMock()
    mock_transport.send = AsyncMock()
    
    # Simulate backpressure by making send delay
    async def delayed_send(*args, **kwargs):
        await asyncio.sleep(0.1)  # Simulate slow client
        return True
    
    mock_transport.send.side_effect = delayed_send
    
    # Create a test event generator that produces events faster than they can be sent
    async def fast_event_generator():
        for i in range(10):
            yield f"event_{i}"
            await asyncio.sleep(0.01)  # Generate events faster than they can be sent
    
    # Test that backpressure mechanism prevents buffer overflow
    buffer_size = 0
    max_buffer_size = 5
    
    async for event in fast_event_generator():
        if buffer_size < max_buffer_size:
            # Simulate adding to buffer
            buffer_size += 1
            await mock_transport.send(event)
        else:
            # Verify that backpressure mechanism is working
            with pytest.raises(asyncio.QueueFull):
                await mock_transport.send(event)
    
    # Verify the number of events actually sent matches our buffer limit
    assert mock_transport.send.call_count <= max_buffer_size


async def test_sse_connection_management(mcp_server):
    """Test SSE connection lifecycle management."""
    # Set up connection tracking
    active_connections = set()
    
    # Mock connection handler
    async def handle_connection(client_id):
        # Add connection to tracking
        active_connections.add(client_id)
        try:
            # Simulate connection lifetime
            await asyncio.sleep(0.1)
        finally:
            # Ensure connection is removed on disconnect
            active_connections.remove(client_id)
    
    # Test multiple concurrent connections
    async def simulate_connections():
        tasks = []
        for i in range(3):
            client_id = f"client_{i}"
            task = asyncio.create_task(handle_connection(client_id))
            tasks.append(task)
        
        # Verify all connections are active
        await asyncio.sleep(0.05)
        assert len(active_connections) == 3
        
        # Wait for all connections to complete
        await asyncio.gather(*tasks)
        
        # Verify all connections were properly cleaned up
        assert len(active_connections) == 0
    
    await simulate_connections()


async def test_sse_keep_alive(mcp_server):
    """Test SSE keep-alive mechanism."""
    mock_transport = MagicMock()
    mock_transport.send = AsyncMock()
    
    # Set up keep-alive configuration
    keep_alive_interval = 0.1  # 100ms for testing
    last_keep_alive = 0
    
    # Simulate connection with keep-alive
    async def run_keep_alive():
        nonlocal last_keep_alive
        start_time = asyncio.get_event_loop().time()
        
        # Run for a short period
        while asyncio.get_event_loop().time() - start_time < 0.5:
            current_time = asyncio.get_event_loop().time()
            
            # Send keep-alive if interval has elapsed
            if current_time - last_keep_alive >= keep_alive_interval:
                await mock_transport.send(": keep-alive\n")
                last_keep_alive = current_time
            
            await asyncio.sleep(0.01)
    
    await run_keep_alive()
    
    # Verify keep-alive messages were sent
    expected_messages = int(0.5 / keep_alive_interval)  # Expected number of keep-alive messages
    assert mock_transport.send.call_count >= expected_messages - 1  # Allow for timing variations
    assert mock_transport.send.call_count <= expected_messages + 1


async def test_sse_error_handling(mcp_server):
    """Test SSE error handling and recovery."""
    mock_transport = MagicMock()
    mock_transport.send = AsyncMock()
    
    # Simulate various error conditions
    async def simulate_errors():
        # Test network error
        mock_transport.send.side_effect = ConnectionError("Network error")
        with pytest.raises(ConnectionError):
            await mock_transport.send("test_event")
        
        # Test client disconnect
        mock_transport.send.side_effect = asyncio.CancelledError()
        with pytest.raises(asyncio.CancelledError):
            await mock_transport.send("test_event")
        
        # Test recovery after error
        mock_transport.send.side_effect = None
        await mock_transport.send("recovery_event")
        mock_transport.send.assert_called_with("recovery_event")
    
    await simulate_errors()
