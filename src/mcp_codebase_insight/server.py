"""Codebase Analysis Server implementation."""

import argparse
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from datetime import datetime
import os
from pathlib import Path

from .core.adr import ADRManager, ADRStatus
from .core.config import ServerConfig
from .core.debug import DebugSystem
from .core.documentation import DocumentationManager
from .core.knowledge import KnowledgeBase
from .core.metrics import MetricsManager
from .core.health import HealthManager
from .core.tasks import TaskManager, TaskStatus, TaskType
from .core.cache import CacheManager
from .core.vector_store import VectorStore
from .core.embeddings import SentenceTransformerEmbedding
from .core.errors import (
    InvalidRequestError,
    ResourceNotFoundError,
    ProcessingError
)
from .utils.logger import get_logger

logger = get_logger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MCP Codebase Insight Server - A tool for analyzing codebases using the Model Context Protocol",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind the server to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port to run the server on"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    return parser.parse_args()

# Create FastAPI app instance
app = FastAPI(
    title="MCP Codebase Insight Server",
    description="Model Context Protocol server for codebase analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

class ToolRequest(BaseModel):
    """Tool request model."""
    name: str
    arguments: Dict

class ToolResponse(BaseModel):
    """Tool response model."""
    content: List[Dict]
    isError: bool = False

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if hasattr(app.state, "health"):
        return await app.state.health.check_health()
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Health manager not initialized")

@app.get("/metrics")
async def get_metrics():
    """Get metrics endpoint."""
    if hasattr(app.state, "metrics"):
        return await app.state.metrics.get_metrics()
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Metrics manager not initialized")

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolRequest) -> ToolResponse:
    """Generic tool endpoint."""
    try:
        if hasattr(app.state, "tasks"):
            tasks = app.state.tasks
        else:
            raise ResourceNotFoundError("Task manager not initialized")
        
        if tool_name == "analyze-code":
            if "code" not in request.arguments:
                raise InvalidRequestError("Missing required field: code")
            
            try:
                task = await tasks.create_task(
                    type="code_analysis",
                    title=f"Code Analysis: {request.arguments.get('context', {}).get('file', 'unknown')}",
                    description="Analyze code for patterns and insights",
                    context=request.arguments
                )
                # Start analysis immediately
                if hasattr(app.state, "kb"):
                    kb = app.state.kb
                else:
                    raise ResourceNotFoundError("Knowledge base not initialized")
                analysis_result = await kb.analyze_code(request.arguments["code"])
                # Update task status
                task = await tasks.update_task(
                    task_id=str(task.id),
                    status=TaskStatus.COMPLETED,
                    result=analysis_result
                )
                return ToolResponse(content=[{
                    "task_id": str(task.id),
                    "results": analysis_result,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }])
            except Exception as e:
                import traceback
                print(f"Error in analyze-code: {str(e)}\n{traceback.format_exc()}")
                raise ProcessingError(f"Error analyzing code: {str(e)}")
        
        elif tool_name == "create-adr":
            required_fields = ["title", "context", "decision"]
            for field in required_fields:
                if field not in request.arguments:
                    raise InvalidRequestError(f"Missing required field: {field}")
            
            try:
                # Convert options with 'name' field to use 'title' field
                options = request.arguments.get("options", [])
                for option in options:
                    if "name" in option and "title" not in option:
                        option["title"] = option.pop("name")
                
                if hasattr(app.state, "adr"):
                    adr = app.state.adr
                else:
                    raise ResourceNotFoundError("ADR manager not initialized")
                adr_doc = await adr.create_adr(
                    title=request.arguments["title"],
                    context=request.arguments["context"],
                    options=options,
                    decision=request.arguments["decision"]
                )
                now = datetime.utcnow()
                return ToolResponse(content=[{
                    "task_id": str(adr_doc.id),
                    "adr_path": f"docs/adrs/{adr_doc.id}.md",
                    "status": ADRStatus.PROPOSED.value,
                    "completed_at": now.isoformat()
                }])
            except Exception as e:
                raise ProcessingError(f"Error creating ADR: {str(e)}")
        
        elif tool_name == "debug-issue":
            required_fields = ["description", "type"]
            for field in required_fields:
                if field not in request.arguments:
                    raise InvalidRequestError(f"Missing required field: {field}")
            
            if hasattr(app.state, "debug"):
                debug = app.state.debug
            else:
                raise ResourceNotFoundError("Debug system not initialized")
            issue = await debug.create_issue(
                title=request.arguments.get("title", "Untitled Issue"),
                type=request.arguments["type"],
                description=request.arguments.get("context", {})
            )
            steps = await debug.analyze_issue(issue.id)
            return ToolResponse(content=[{
                "task_id": str(issue.id),
                "steps": steps
            }])
        
        elif tool_name == "search-knowledge":
            if "query" not in request.arguments:
                raise InvalidRequestError("Missing required field: query")
            
            if hasattr(app.state, "kb"):
                kb = app.state.kb
            else:
                raise ResourceNotFoundError("Knowledge base not initialized")
            results = await kb.find_similar_patterns(
                query=request.arguments["query"],
                pattern_type=request.arguments.get("type"),
                limit=request.arguments.get("limit", 5)
            )
            return ToolResponse(content=[{
                "patterns": [r.dict() for r in results]
            }])
        
        elif tool_name == "crawl-docs":
            required_fields = ["urls", "source_type"]
            for field in required_fields:
                if field not in request.arguments:
                    raise InvalidRequestError(f"Missing required field: {field}")
            
            try:
                task = await tasks.create_task(
                    type=TaskType.DOCUMENTATION_CRAWL,
                    title=f"Documentation Crawl: {request.arguments['source_type']}",
                    description="Crawl documentation for insights",
                    context=request.arguments
                )
                # Start crawling immediately
                if hasattr(app.state, "docs_manager"):
                    docs_manager = app.state.docs_manager
                else:
                    raise ResourceNotFoundError("Documentation manager not initialized")
                try:
                    docs = await docs_manager.crawl_docs(
                        urls=request.arguments["urls"],
                        source_type=request.arguments["source_type"]
                    )
                    # Update task with results
                    task = await tasks.update_task(
                        task_id=str(task.id),
                        status=TaskStatus.COMPLETED,
                        result={
                            "documents": [doc.model_dump() for doc in docs],
                            "total_documents": len(docs)
                        }
                    )
                    return ToolResponse(content=[{
                        "task_id": str(task.id),
                        "docs_stored": len(docs),
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None
                    }])
                except Exception as e:
                    import traceback
                    print(f"Error in crawl-docs: {str(e)}\n{traceback.format_exc()}")
                    # Update task with error
                    await tasks.update_task(
                        task_id=str(task.id),
                        status=TaskStatus.FAILED,
                        error=str(e)
                    )
                    raise ProcessingError(f"Error crawling docs: {str(e)}")
            except Exception as e:
                import traceback
                print(f"Error in crawl-docs task creation: {str(e)}\n{traceback.format_exc()}")
                raise ProcessingError(f"Error in crawl-docs task: {str(e)}")
        
        elif tool_name == "get-task":
            if "task_id" not in request.arguments:
                raise InvalidRequestError("Missing required field: task_id")
            
            task = await tasks.get_task(request.arguments["task_id"])
            if not task:
                raise ResourceNotFoundError("Task not found")
            
            return ToolResponse(content=[{
                "task_id": str(task.id),
                "type": task.type,
                "status": task.status,
                "result": task.result,
                "error": task.error,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }])
        
        else:
            raise ResourceNotFoundError(f"Unknown tool: {tool_name}")
            
    except InvalidRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.on_event("startup")
async def startup():
    """Initialize server components on startup."""
    # Initialize config
    config = ServerConfig()
    
    # Ensure directories exist
    os.makedirs(config.docs_cache_dir, exist_ok=True)
    os.makedirs(config.adr_dir, exist_ok=True)
    os.makedirs(config.kb_storage_dir, exist_ok=True)
    os.makedirs(config.disk_cache_dir, exist_ok=True)
    
    # Initialize components
    app.state.config = config
    app.state.metrics = MetricsManager(config)
    app.state.health = HealthManager(config)
    app.state.cache = CacheManager(config)
    app.state.debug = DebugSystem(config)
    app.state.docs_manager = DocumentationManager(config)
    app.state.adr = ADRManager(config)

    # Initialize vector store with embedder
    embedder = SentenceTransformerEmbedding()
    app.state.vector_store = VectorStore(
        url=config.qdrant_url,
        embedder=embedder
    )
    app.state.kb = KnowledgeBase(config, vector_store=app.state.vector_store)

    app.state.tasks = TaskManager(
        config=config,
        adr_manager=app.state.adr,
        debug_system=app.state.debug,
        doc_manager=app.state.docs_manager,
        knowledge_base=app.state.kb
    )
    
    logger.info(
        "Server initialized",
        host=config.host,
        port=config.port,
        docs_dir=str(config.docs_cache_dir),
        kb_dir=str(config.kb_storage_dir)
    )

@app.on_event("shutdown")
async def shutdown():
    """Cleanup server components on shutdown."""
    if hasattr(app.state, "vector_store"):
        await app.state.vector_store.close()
    if hasattr(app.state, "cache"):
        await app.state.cache.clear_all()
    if hasattr(app.state, "metrics"):
        await app.state.metrics.reset()

def run():
    """Run the server."""
    args = parse_args()
    
    # Update config with command line arguments
    if hasattr(app.state, "config"):
        app.state.config.host = args.host
        app.state.config.port = args.port
        app.state.config.log_level = args.log_level
        app.state.config.debug_mode = args.debug
    
    # Log startup message
    logger.info(
        "Starting MCP Codebase Insight Server",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        debug=args.debug
    )
    
    import uvicorn
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level.lower(),
        reload=args.debug
    )

if __name__ == "__main__":
    run()
