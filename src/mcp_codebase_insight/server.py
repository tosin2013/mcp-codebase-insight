"""Codebase Analysis Server implementation."""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from datetime import datetime

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

# Create FastAPI app instance
app = FastAPI(
    title="MCP Codebase Insight Server",
    description="Model Context Protocol server for codebase analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize config
config = ServerConfig()

# Initialize components
metrics = MetricsManager(config)
health = HealthManager(config)
cache = CacheManager(config)
debug = DebugSystem(config)
docs_manager = DocumentationManager(config)
adr = ADRManager(config)

# Initialize vector store with embedder
embedder = SentenceTransformerEmbedding()
vector_store = VectorStore(
    url=config.qdrant_url,
    embedder=embedder
)
kb = KnowledgeBase(config, vector_store=vector_store)

tasks = TaskManager(
    config=config,
    adr_manager=adr,
    debug_system=debug,
    doc_manager=docs_manager,
    knowledge_base=kb
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
    return await health.check_health()

@app.get("/metrics")
async def get_metrics():
    """Get metrics endpoint."""
    return await metrics.get_metrics()

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolRequest) -> ToolResponse:
    """Generic tool endpoint."""
    try:
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
    """Initialize components on startup."""
    await vector_store.initialize()
    await kb.initialize()
    await metrics.initialize()
    await health.initialize()

@app.on_event("shutdown")
async def shutdown():
    """Cleanup components on shutdown."""
    await kb.cleanup()
    await metrics.cleanup()
    await health.cleanup()
