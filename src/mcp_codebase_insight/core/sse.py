"""Server-Sent Events (SSE) transport implementation for MCP."""

import asyncio
import logging
import json
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse, StreamingResponse
import uuid
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from starlette.middleware.cors import CORSMiddleware

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from ..utils.logger import get_logger

logger = get_logger(__name__)

async def send_heartbeats(queue: asyncio.Queue, interval: int = 30):
    """Send periodic heartbeat messages to keep the connection alive.
    
    Args:
        queue: The queue to send heartbeats to
        interval: Time between heartbeats in seconds
    """
    while True:
        try:
            await queue.put({"type": "heartbeat", "timestamp": datetime.now(timezone.utc).isoformat()})
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            await asyncio.sleep(1)  # Brief pause before retrying

class CodebaseInsightSseTransport(SseServerTransport):
    """Custom SSE transport implementation for Codebase Insight."""
    
    def __init__(self, endpoint: str):
        """Initialize the SSE transport.
        
        Args:
            endpoint: The endpoint path for SSE connections
        """
        super().__init__(endpoint)
        self.connections = {}
        self.message_queue = asyncio.Queue()
        logger.info(f"Initializing SSE transport with endpoint: {endpoint}")
        
    async def handle_sse(self, request: Request) -> StreamingResponse:
        """Handle incoming SSE connection requests.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            StreamingResponse for the SSE connection
        """
        connection_id = str(uuid.uuid4())
        queue = asyncio.Queue()
        self.connections[connection_id] = queue
        
        logger.info(f"New SSE connection established: {connection_id}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Active connections: {len(self.connections)}")
        
        async def event_generator():
            try:
                logger.debug(f"Starting event generator for connection {connection_id}")
                heartbeat_task = asyncio.create_task(send_heartbeats(queue))
                logger.debug(f"Heartbeat task started for connection {connection_id}")
                
                while True:
                    try:
                        message = await queue.get()
                        logger.debug(f"Connection {connection_id} received message: {message}")
                        
                        if isinstance(message, dict):
                            data = json.dumps(message)
                        else:
                            data = str(message)
                            
                        yield f"data: {data}\n\n"
                        logger.debug(f"Sent message to connection {connection_id}")
                        
                    except asyncio.CancelledError:
                        logger.info(f"Event generator cancelled for connection {connection_id}")
                        break
                    except Exception as e:
                        logger.error(f"Error in event generator for connection {connection_id}: {e}")
                        break
                        
            finally:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
                    
                if connection_id in self.connections:
                    del self.connections[connection_id]
                logger.info(f"Event generator cleaned up for connection {connection_id}")
                logger.debug(f"Remaining active connections: {len(self.connections)}")
                
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",  # Allow CORS
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET, POST"
            }
        )
        
    async def handle_message(self, request: Request) -> Response:
        """Handle incoming messages to be broadcast over SSE.
        
        Args:
            request: The incoming HTTP request with the message
            
        Returns:
            HTTP response indicating message handling status
        """
        try:
            message = await request.json()
            
            # Broadcast to all connections
            for queue in self.connections.values():
                await queue.put(message)
                
            return JSONResponse({"status": "message sent"})
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return JSONResponse(
                {"error": str(e)},
                status_code=500
            )
            
    async def send(self, message: Any) -> None:
        """Send a message to all connected clients.
        
        Args:
            message: The message to send
        """
        # Put message in queue for all connections
        for queue in self.connections.values():
            await queue.put(message)
            
    async def broadcast(self, message: Any) -> None:
        """Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast
        """
        await self.send(message)
        
    async def connect(self) -> Tuple[MemoryObjectReceiveStream, MemoryObjectSendStream]:
        """Create a new SSE connection.
        
        Returns:
            Tuple of receive and send streams for the connection
        """
        # Create memory object streams for this connection
        receive_stream = MemoryObjectReceiveStream()
        send_stream = MemoryObjectSendStream()
        
        # Store the connection
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = send_stream
        
        return receive_stream, send_stream
        
    async def disconnect(self, connection_id: str) -> None:
        """Disconnect a client.
        
        Args:
            connection_id: The ID of the connection to disconnect
        """
        if connection_id in self.connections:
            del self.connections[connection_id]
            logger.info(f"Disconnected client: {connection_id}")

async def verify_routes(app: Starlette) -> Dict[str, List[str]]:
    """Verify and log all registered routes in the application.
    
    Args:
        app: The Starlette application to verify
        
    Returns:
        Dictionary mapping route paths to their methods
    """
    routes = {}
    for route in app.routes:
        if isinstance(route, Mount):
            logger.info(f"Mount point: {route.path}")
            # Recursively verify mounted routes
            mounted_routes = await verify_routes(route.app)
            for path, methods in mounted_routes.items():
                full_path = f"{route.path}{path}"
                routes[full_path] = methods
        else:
            routes[route.path] = route.methods
            logger.info(f"Route: {route.path}, methods: {route.methods}")
    return routes

def create_sse_server(mcp_server: Optional[FastMCP] = None) -> Starlette:
    """Create an SSE server instance.
    
    Args:
        mcp_server: Optional FastMCP instance to use. If not provided, a new one will be created.
        
    Returns:
        Starlette application configured for SSE
    """
    app = Starlette(debug=True)  # Enable debug mode for better error reporting
    
    # Create SSE transport
    transport = CodebaseInsightSseTransport("/sse")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    async def health_check(request: Request) -> JSONResponse:
        """Health check endpoint."""
        return JSONResponse({
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "connections": len(transport.connections)
        })
    
    # Add routes
    app.add_route("/health", health_check, methods=["GET"])
    app.add_route("/sse", transport.handle_sse, methods=["GET"])
    app.add_route("/message", transport.handle_message, methods=["POST"])
    
    logger.info("Created SSE server with routes:")
    asyncio.create_task(verify_routes(app))
    
    return app

class MCP_CodebaseInsightServer:
    """MCP server implementation for Codebase Insight.
    
    This class manages the Model Context Protocol server, connecting it to
    the Codebase Insight's core components and exposing them as MCP tools.
    """
    
    def __init__(self, server_state):
        """Initialize the MCP server with access to the application state.
        
        Args:
            server_state: The global server state providing access to components
        """
        self.state = server_state
        self.mcp_server = FastMCP(name="MCP-Codebase-Insight")
        self.tools_registered = False
        self._starlette_app = None  # Cache the Starlette app
        logger.info("MCP Codebase Insight server initialized")
        
    async def cleanup(self):
        """Clean up resources used by the MCP server.
        
        This method ensures proper shutdown of the MCP server and
        releases any resources it might be holding.
        """
        logger.info("Cleaning up MCP server resources")
        # If the MCP server has a shutdown or cleanup method, call it here
        # For now, just log the cleanup attempt
        self.tools_registered = False
        self._starlette_app = None
        logger.info("MCP server cleanup completed")
    
    def is_initialized(self) -> bool:
        """Check if the MCP server is properly initialized.
        
        Returns:
            True if the server is initialized and ready to use, False otherwise
        """
        return self.tools_registered and self._starlette_app is not None
        
    def register_tools(self):
        """Register all available tools with the MCP server.
        
        This connects the MCP protocol to the Codebase Insight core components,
        exposing their functionality through the MCP interface.
        """
        if self.tools_registered:
            logger.debug("Tools already registered, skipping")
            return
            
        logger.info("Registering tools with MCP server")
        
        # Check if critical dependencies are available
        critical_dependencies = ["vector_store", "knowledge_base", "task_manager", "adr_manager"]
        missing_dependencies = []
        
        for dependency in critical_dependencies:
            if not self.state.get_component(dependency):
                missing_dependencies.append(dependency)
                
        if missing_dependencies:
            logger.warning(f"Some critical dependencies are not available: {', '.join(missing_dependencies)}")
            logger.warning("Tools requiring these dependencies will not be registered")
            # Don't fail registration completely - continue with available tools
        
        # Register available tools
        try:
            self._register_vector_search()
            self._register_knowledge()
            self._register_adr()
            self._register_task()
            
            # Mark tools as registered even if some failed
            self.tools_registered = True
            logger.info("MCP tools registration completed")
        except Exception as e:
            logger.error(f"Error registering MCP tools: {e}", exc_info=True)
            # Don't mark as registered if there was an error
        
    def _register_vector_search(self):
        """Register the vector search tool with the MCP server."""
        vector_store = self.state.get_component("vector_store")
        if not vector_store:
            logger.warning("Vector store component not available, skipping tool registration")
            return
            
        # Verify that the vector store is properly initialized
        if not hasattr(vector_store, 'search') or not callable(getattr(vector_store, 'search')):
            logger.warning("Vector store component does not have a search method, skipping tool registration")
            return
            
        async def vector_search(query: str, limit: int = 5, threshold: float = 0.7, 
                          file_type: Optional[str] = None, path_pattern: Optional[str] = None):
            """Search for code snippets semantically similar to the query text."""
            logger.debug(f"MCP vector search request: {query=}, {limit=}, {threshold=}")
            
            # Prepare filters if provided
            filter_conditions = {}
            if file_type:
                filter_conditions["file_type"] = {"$eq": file_type}
            if path_pattern:
                filter_conditions["path"] = {"$like": path_pattern}
                
            results = await vector_store.search(
                text=query,
                filter_conditions=filter_conditions if filter_conditions else None,
                limit=limit
            )
            
            # Format results
            formatted_results = [
                {
                    "id": result.id,
                    "score": result.score,
                    "text": result.metadata.get("text", ""),
                    "file_path": result.metadata.get("file_path", ""),
                    "line_range": result.metadata.get("line_range", ""),
                    "type": result.metadata.get("type", "code"),
                    "language": result.metadata.get("language", ""),
                    "timestamp": result.metadata.get("timestamp", "")
                }
                for result in results
                if result.score >= threshold
            ]
            
            return {"results": formatted_results}
            
        self.mcp_server.add_tool(
            name="vector-search",
            fn=vector_search,
            description="Search for code snippets semantically similar to the query text"
        )
        logger.debug("Vector search tool registered")
        
    def _register_knowledge(self):
        """Register the knowledge base tool with the MCP server."""
        knowledge_base = self.state.get_component("knowledge_base")
        if not knowledge_base:
            logger.warning("Knowledge base component not available, skipping tool registration")
            return
            
        async def search_knowledge(query: str, pattern_type: str = "code", limit: int = 5):
            """Search for patterns in the knowledge base."""
            logger.debug(f"MCP knowledge search request: {query=}, {pattern_type=}, {limit=}")
            
            results = await knowledge_base.search_patterns(
                query=query,
                pattern_type=pattern_type,
                limit=limit
            )
            
            # Format results
            formatted_results = [
                {
                    "id": result.id,
                    "pattern": result.pattern,
                    "description": result.description,
                    "type": result.type,
                    "confidence": result.confidence,
                    "metadata": result.metadata
                }
                for result in results
            ]
            
            return {"results": formatted_results}
            
        self.mcp_server.add_tool(
            name="knowledge-search",
            fn=search_knowledge,
            description="Search for patterns in the knowledge base"
        )
        logger.debug("Knowledge search tool registered")
        
    def _register_adr(self):
        """Register the ADR management tool with the MCP server."""
        adr_manager = self.state.get_component("adr_manager")
        if not adr_manager:
            logger.warning("ADR manager component not available, skipping tool registration")
            return
            
        async def list_adrs(status: Optional[str] = None, limit: int = 10):
            """List architectural decision records."""
            logger.debug(f"MCP ADR list request: {status=}, {limit=}")
            
            try:
                adrs = await adr_manager.list_adrs(status=status, limit=limit)
                
                # Format results
                formatted_results = [
                    {
                        "id": adr.id,
                        "title": adr.title,
                        "status": adr.status,
                        "date": adr.date.isoformat() if adr.date else None,
                        "authors": adr.authors,
                        "summary": adr.summary
                    }
                    for adr in adrs
                ]
                
                return {"adrs": formatted_results}
            except Exception as e:
                logger.error(f"Error listing ADRs: {e}", exc_info=True)
                return {"error": str(e), "adrs": []}
                
        self.mcp_server.add_tool(
            name="adr-list",
            fn=list_adrs,
            description="List architectural decision records"
        )
        logger.debug("ADR management tool registered")
        
    def _register_task(self):
        """Register the task management tool with the MCP server."""
        task_tracker = self.state.get_component("task_tracker")
        if not task_tracker:
            logger.warning("Task tracker component not available, skipping tool registration")
            return
            
        async def get_task_status(task_id: str):
            """Get the status of a specific task."""
            logger.debug(f"MCP task status request: {task_id=}")
            
            try:
                status = await task_tracker.get_task_status(task_id)
                return status
            except Exception as e:
                logger.error(f"Error getting task status: {e}", exc_info=True)
                return {"error": str(e), "status": "unknown"}
                
        self.mcp_server.add_tool(
            name="task-status",
            fn=get_task_status,
            description="Get the status of a specific task"
        )
        logger.debug("Task management tool registered")
        
    def get_starlette_app(self) -> Starlette:
        """Get the Starlette application for the MCP server.
        
        Returns:
            Configured Starlette application
        """
        # Ensure tools are registered
        self.register_tools()
        
        # Create and return the Starlette app for SSE
        if self._starlette_app is None:
            self._starlette_app = create_sse_server(self.mcp_server)
        return self._starlette_app
