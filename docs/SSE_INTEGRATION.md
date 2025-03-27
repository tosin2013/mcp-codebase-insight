# Server-Sent Events (SSE) Integration

This document explains the Server-Sent Events (SSE) integration in the MCP Codebase Insight server, including its purpose, architecture, and usage instructions.

## Overview

The SSE integration enables real-time, bidirectional communication between the MCP Codebase Insight server and clients using the Model Context Protocol (MCP). This allows clients to receive live updates for long-running operations and establish persistent connections for continuous data flow.

## Architecture

The SSE integration is built as a modular component within the MCP Codebase Insight system, following these design principles:

1. **Separation of Concerns**: The SSE transport layer is isolated from the core application logic
2. **Non-Interference**: SSE endpoints operate alongside existing REST API endpoints without disruption
3. **Shared Resources**: Both REST and SSE interfaces use the same underlying components and state

### Key Components

- **MCP_CodebaseInsightServer**: Manages the MCP protocol server and exposes system functionality as MCP tools
- **FastMCP**: The core MCP protocol implementation that handles messaging format and protocol features
- **SseServerTransport**: Implements the SSE protocol for persistent connections
- **Starlette Integration**: Low-level ASGI application that handles SSE connections

### Endpoint Structure

- `/mcp/sse/`: Establishes the SSE connection for real-time events
- `/mcp/messages/`: Handles incoming messages from clients via HTTP POST

### Data Flow

```
Client  <--->  SSE Connection (/mcp/sse/)  <--->  MCP Server  <--->  Core Components
       <--->  Message POST (/mcp/messages/)  <--/
```

## Available Tools

The SSE integration exposes these core system capabilities as MCP tools:

1. **vector-search**: Search for code snippets semantically similar to a query text
2. **knowledge-search**: Search for patterns in the knowledge base
3. **adr-list**: Retrieve architectural decision records
4. **task-status**: Check status of long-running tasks

## Usage Instructions

### Client Configuration

To connect to the SSE endpoint, configure your MCP client as follows:

```json
{
  "mcpClients": {
    "codebase-insight-sse": {
      "url": "http://localhost:8000/mcp",
      "transport": "sse"
    }
  }
}
```

### Example: Connecting with MCP Client

```python
from mcp.client import Client

# Connect to the SSE endpoint
client = Client.connect("codebase-insight-sse")

# Use vector search tool
results = await client.call_tool(
    "vector-search", 
    {"query": "function that parses JSON", "limit": 5}
)
```

## Testing

The SSE implementation includes tests to verify:

1. Connection establishment and maintenance
2. Tool registration and execution
3. Error handling and reconnection behavior

Run SSE-specific tests with:

```bash
pytest tests/integration/test_sse.py -v
```

## Security Considerations

The SSE integration inherits the security model of the main application. When security features like authentication are enabled, they apply to SSE connections as well.

## Performance Considerations

SSE connections are persistent and can consume server resources. Consider these guidelines:

- Implement client-side reconnection strategies with exponential backoff
- Set reasonable timeouts for idle connections
- Monitor connection counts in production environments

## Troubleshooting

Common issues and solutions:

1. **Connection Refused**: Ensure the server is running and the client is using the correct URL
2. **Invalid SSE Format**: Check for middleware that might buffer responses
3. **Connection Drops**: Verify network stability and implement reconnection logic
