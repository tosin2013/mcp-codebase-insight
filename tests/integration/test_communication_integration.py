import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from tests.components.test_stdio_components import MockStdinReader, MockStdoutWriter

class MockSSEClient:
    def __init__(self):
        self.events = []
        self.connected = True
    
    async def send(self, event):
        if not self.connected:
            raise ConnectionError("Client disconnected")
        self.events.append(event)
    
    def disconnect(self):
        self.connected = False

@pytest.fixture
async def mock_communication_setup():
    """Set up mock stdio and SSE components for integration testing."""
    # Set up stdio mocks
    stdio_reader = MockStdinReader("")
    stdio_writer = MockStdoutWriter()
    
    # Set up SSE mock
    sse_client = MockSSEClient()
    
    return stdio_reader, stdio_writer, sse_client

async def test_tool_registration_with_sse_notification(mock_communication_setup):
    """Test tool registration process with SSE notification."""
    stdio_reader, stdio_writer, sse_client = mock_communication_setup
    
    # Simulate tool registration via stdio
    registration_message = {
        "type": "register",
        "tool_id": "test_tool",
        "capabilities": ["capability1", "capability2"]
    }
    
    # Override reader's input with registration message
    stdio_reader.input_stream.write(json.dumps(registration_message) + "\n")
    stdio_reader.input_stream.seek(0)
    
    # Process registration
    line = await stdio_reader.readline()
    message = json.loads(line)
    
    # Send registration acknowledgment via stdio
    response = {
        "type": "registration_success",
        "tool_id": message["tool_id"]
    }
    await stdio_writer.write(json.dumps(response) + "\n")
    
    # Send SSE notification about new tool
    sse_notification = {
        "type": "tool_registered",
        "tool_id": message["tool_id"],
        "capabilities": message["capabilities"]
    }
    await sse_client.send(json.dumps(sse_notification))
    
    # Verify stdio response
    assert "registration_success" in stdio_writer.get_output()
    
    # Verify SSE notification
    assert len(sse_client.events) == 1
    assert "tool_registered" in sse_client.events[0]
    assert message["tool_id"] in sse_client.events[0]

async def test_bidirectional_communication(mock_communication_setup):
    """Test bidirectional communication between stdio and SSE."""
    stdio_reader, stdio_writer, sse_client = mock_communication_setup
    
    # Set up test message flow
    stdio_messages = [
        {"type": "request", "id": "1", "method": "test", "data": "stdio_data"},
        {"type": "request", "id": "2", "method": "test", "data": "more_data"}
    ]
    
    # Write messages to stdio
    for msg in stdio_messages:
        stdio_reader.input_stream.write(json.dumps(msg) + "\n")
    stdio_reader.input_stream.seek(0)
    
    # Process messages and generate SSE events
    while True:
        line = await stdio_reader.readline()
        if not line:
            break
        
        # Process stdio message
        message = json.loads(line)
        
        # Generate SSE event
        sse_event = {
            "type": "event",
            "source": "stdio",
            "data": message["data"]
        }
        await sse_client.send(json.dumps(sse_event))
        
        # Send response via stdio
        response = {
            "type": "response",
            "id": message["id"],
            "status": "success"
        }
        await stdio_writer.write(json.dumps(response) + "\n")
    
    # Verify all messages were processed
    assert len(sse_client.events) == len(stdio_messages)
    assert all("stdio" in event for event in sse_client.events)
    
    # Verify stdio responses
    output = stdio_writer.get_output()
    responses = [json.loads(line) for line in output.strip().split("\n")]
    assert len(responses) == len(stdio_messages)
    assert all(resp["type"] == "response" for resp in responses)

async def test_error_propagation(mock_communication_setup):
    """Test error propagation between stdio and SSE."""
    stdio_reader, stdio_writer, sse_client = mock_communication_setup
    
    # Simulate error in stdio
    error_message = {
        "type": "request",
        "id": "error_test",
        "method": "test",
        "data": "error_data"
    }
    stdio_reader.input_stream.write(json.dumps(error_message) + "\n")
    stdio_reader.input_stream.seek(0)
    
    # Process message and simulate error
    line = await stdio_reader.readline()
    message = json.loads(line)
    
    # Generate error response in stdio
    error_response = {
        "type": "error",
        "id": message["id"],
        "error": "Test error occurred"
    }
    await stdio_writer.write(json.dumps(error_response) + "\n")
    
    # Propagate error to SSE
    sse_error_event = {
        "type": "error_event",
        "source": "stdio",
        "error": "Test error occurred",
        "request_id": message["id"]
    }
    await sse_client.send(json.dumps(sse_error_event))
    
    # Verify error handling
    assert "error" in stdio_writer.get_output()
    assert len(sse_client.events) == 1
    assert "error_event" in sse_client.events[0]

async def test_connection_state_handling(mock_communication_setup):
    """Test handling of connection state changes."""
    stdio_reader, stdio_writer, sse_client = mock_communication_setup
    
    # Test normal operation
    test_message = {
        "type": "request",
        "id": "state_test",
        "method": "test"
    }
    stdio_reader.input_stream.write(json.dumps(test_message) + "\n")
    stdio_reader.input_stream.seek(0)
    
    # Process message while connected
    line = await stdio_reader.readline()
    message = json.loads(line)
    await sse_client.send(json.dumps({"type": "event", "data": "test"}))
    
    # Simulate SSE client disconnect
    sse_client.disconnect()
    
    # Attempt to send message after disconnect
    with pytest.raises(ConnectionError):
        await sse_client.send(json.dumps({"type": "event", "data": "test"}))
    
    # Send disconnect notification via stdio
    disconnect_notification = {
        "type": "notification",
        "event": "client_disconnected"
    }
    await stdio_writer.write(json.dumps(disconnect_notification) + "\n")
    
    # Verify disconnect handling
    assert "client_disconnected" in stdio_writer.get_output()
    assert not sse_client.connected 