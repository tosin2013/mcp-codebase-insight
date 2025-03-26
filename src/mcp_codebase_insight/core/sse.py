"""Server-Sent Events (SSE) transport implementation for MCP."""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_sse_server(mcp_server: FastMCP) -> Starlette:
    """Create a Starlette application that handles SSE connections and message handling.
    
    This function initializes an SSE transport layer for the MCP protocol,
    providing real-time communication capabilities through Server-Sent Events.
    
    Args:
        mcp_server: The FastMCP instance to connect to the SSE transport
        
    Returns:
        A Starlette application configured to handle SSE connections
    """
    logger.info("Creating SSE server transport layer")
    transport = SseServerTransport("/messages/")
    
    async def handle_sse(request):
        """Handle incoming SSE connections.
        
        This function establishes an SSE connection with the client and connects
        it to the MCP server for bidirectional communication.
        """
        logger.info(f"New SSE connection request from {request.client}")
        try:
            async with transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                logger.debug("SSE connection established, starting MCP server")
                # Updated for MCP v1.5.0 which doesn't use create_initialization_options
                await mcp_server.run(
                    streams[0], 
                    streams[1]
                )
        except Exception as e:
            logger.error(f"Error in SSE connection: {e}", exc_info=True)
            raise
            
    # Create Starlette routes for SSE and message handling
    routes = [
        Route("/sse/", endpoint=handle_sse),
        Mount("/messages/", app=transport.handle_post_message),
    ]
    
    logger.debug("SSE server transport layer created with routes: /sse/ and /messages/")
    return Starlette(routes=routes)


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
        self.mcp_server = FastMCP("MCP-Codebase-Insight")
        self.tools_registered = False
        logger.info("MCP Codebase Insight server initialized")
        
    def register_tools(self):
        """Register all available tools with the MCP server.
        
        This connects the MCP protocol to the Codebase Insight core components,
        exposing their functionality through the MCP interface.
        """
        if self.tools_registered:
            logger.debug("Tools already registered, skipping")
            return
            
        logger.info("Registering tools with MCP server")
        
        # Vector Store Search Tool
        self._register_vector_search_tool()
        
        # Knowledge Base Tool
        self._register_knowledge_tool()
        
        # ADR Management Tool
        self._register_adr_tool()
        
        # Task Management Tool
        self._register_task_tool()
        
        self.tools_registered = True
        logger.info("All tools registered with MCP server")
        
    def _register_vector_search_tool(self):
        """Register the vector search tool with the MCP server."""
        vector_store = self.state.get_component("vector_store")
        if not vector_store:
            logger.warning("Vector store component not available, skipping tool registration")
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
        
    def _register_knowledge_tool(self):
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
        
    def _register_adr_tool(self):
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
        
    def _register_task_tool(self):
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
            A Starlette application handling SSE connections for the MCP server
        """
        # Ensure tools are registered
        self.register_tools()
        
        # Create and return the Starlette app for SSE
        return create_sse_server(self.mcp_server)
