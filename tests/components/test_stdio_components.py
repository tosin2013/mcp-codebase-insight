import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from io import StringIO

class MockStdinReader:
    def __init__(self, input_data):
        self.input_stream = StringIO(input_data)
    
    async def readline(self):
        return self.input_stream.readline()

class MockStdoutWriter:
    def __init__(self):
        self.output = StringIO()
    
    async def write(self, data):
        self.output.write(data)
    
    async def drain(self):
        pass
    
    def get_output(self):
        return self.output.getvalue()

@pytest.fixture
def mock_stdio():
    input_data = '{"type": "register", "tool_id": "test_tool"}\n'
    reader = MockStdinReader(input_data)
    writer = MockStdoutWriter()
    return reader, writer

async def test_stdio_tool_registration(mock_stdio):
    """Test tool registration via stdio."""
    reader, writer = mock_stdio
    
    # Process registration message
    line = await reader.readline()
    message = json.loads(line)
    
    # Verify registration message format
    assert message["type"] == "register"
    assert message["tool_id"] == "test_tool"
    
    # Send registration acknowledgment
    response = {
        "type": "registration_success",
        "tool_id": message["tool_id"]
    }
    await writer.write(json.dumps(response) + "\n")
    
    # Verify response was written
    assert "registration_success" in writer.get_output()
    assert message["tool_id"] in writer.get_output()

async def test_stdio_message_streaming():
    """Test streaming messages via stdio."""
    # Set up mock streams with multiple messages
    input_messages = [
        {"type": "request", "id": "1", "method": "test", "params": {}},
        {"type": "request", "id": "2", "method": "test", "params": {}}
    ]
    input_data = "\n".join(json.dumps(msg) for msg in input_messages) + "\n"
    
    reader = MockStdinReader(input_data)
    writer = MockStdoutWriter()
    
    # Process messages
    messages_received = []
    while True:
        line = await reader.readline()
        if not line:
            break
        messages_received.append(json.loads(line))
    
    # Verify all messages were received
    assert len(messages_received) == len(input_messages)
    assert all(msg["type"] == "request" for msg in messages_received)

async def test_stdio_error_handling():
    """Test error handling in stdio communication."""
    # Test invalid JSON
    reader = MockStdinReader("invalid json\n")
    writer = MockStdoutWriter()
    
    line = await reader.readline()
    try:
        message = json.loads(line)
    except json.JSONDecodeError as e:
        error_response = {
            "type": "error",
            "error": "Invalid JSON format"
        }
        await writer.write(json.dumps(error_response) + "\n")
    
    assert "error" in writer.get_output()
    assert "Invalid JSON format" in writer.get_output()

async def test_stdio_message_ordering():
    """Test message ordering and response correlation."""
    # Set up messages with sequence numbers
    input_messages = [
        {"type": "request", "id": "1", "sequence": 1},
        {"type": "request", "id": "2", "sequence": 2},
        {"type": "request", "id": "3", "sequence": 3}
    ]
    input_data = "\n".join(json.dumps(msg) for msg in input_messages) + "\n"
    
    reader = MockStdinReader(input_data)
    writer = MockStdoutWriter()
    
    # Process messages and send responses
    sequence = 1
    while True:
        line = await reader.readline()
        if not line:
            break
        
        message = json.loads(line)
        assert message["sequence"] == sequence
        
        response = {
            "type": "response",
            "id": message["id"],
            "sequence": sequence
        }
        await writer.write(json.dumps(response) + "\n")
        sequence += 1
    
    # Verify response ordering
    output = writer.get_output()
    responses = [json.loads(line) for line in output.strip().split("\n")]
    assert all(resp["sequence"] == idx + 1 for idx, resp in enumerate(responses))

async def test_stdio_large_message_handling():
    """Test handling of large messages via stdio."""
    # Create a large message
    large_data = "x" * 1024 * 1024  # 1MB of data
    large_message = {
        "type": "request",
        "id": "large",
        "data": large_data
    }
    
    reader = MockStdinReader(json.dumps(large_message) + "\n")
    writer = MockStdoutWriter()
    
    # Process large message
    line = await reader.readline()
    message = json.loads(line)
    
    # Verify message was received correctly
    assert len(message["data"]) == len(large_data)
    assert message["data"] == large_data
    
    # Send large response
    response = {
        "type": "response",
        "id": message["id"],
        "data": large_data
    }
    await writer.write(json.dumps(response) + "\n")
    
    # Verify large response was written
    output = writer.get_output()
    response_message = json.loads(output)
    assert len(response_message["data"]) == len(large_data) 