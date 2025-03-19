from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.adr import ADRManager, ADRStatus
from mcp_codebase_insight.core.debug import DebugSystem, IssueType, IssueStatus
from mcp_codebase_insight.core.documentation import DocumentationManager
from mcp_codebase_insight.core.knowledge import KnowledgeBase, PatternType
from mcp_codebase_insight.core.vector_store import VectorStore
from mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding
from mcp_codebase_insight.core.prompts import PromptManager, PromptType, PromptContext
from mcp_codebase_insight.core.tasks import TaskManager, TaskType, TaskPriority, TaskStatus
from mcp_codebase_insight.utils.logger import get_logger

logger = get_logger(__name__)

class ToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolResponse(BaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False

class CodebaseAnalysisServer:
    """MCP server for codebase analysis."""

    def __init__(self, config: ServerConfig):
        """Initialize server components."""
        self.config = config
        self.app = FastAPI()

        # Initialize Qdrant client and vector store
        from qdrant_client import QdrantClient

        client = QdrantClient(url=config.qdrant_url)
        embedder = SentenceTransformerEmbedding(config.embedding_model)
        vector_store = VectorStore(client, embedder, config.collection_name)
        
        # Initialize core components
        self.adr_manager = ADRManager(config)
        self.debug_system = DebugSystem(config)
        self.doc_manager = DocumentationManager(config)
        self.knowledge_base = KnowledgeBase(config, vector_store)
        self.prompt_manager = PromptManager(config, self.knowledge_base)
        self.task_manager = TaskManager(
            config,
            self.adr_manager,
            self.debug_system,
            self.doc_manager,
            self.knowledge_base,
            self.prompt_manager
        )
        
        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register API endpoints for tools."""
        @self.app.post("/tools/analyze-code")
        async def analyze_code(request: ToolRequest) -> ToolResponse:
            code = request.arguments.get("code", "")
            context = request.arguments.get("context", {})
            """Analyze code for patterns and architectural insights."""
            if not code.strip():
                return ToolResponse(
                    content=[{
                        "error": "Code cannot be empty"
                    }],
                    isError=True
                )
            try:
                task = await self.task_manager.create_task(
                    type=TaskType.CODE_ANALYSIS,
                    title="Code Analysis",
                    description=f"Analyze code patterns and architecture",
                    priority=TaskPriority.MEDIUM,
                    context={
                        "code": code,
                        **(context or {})
                    }
                )
                
                for step in task.steps:
                    task = await self.task_manager.execute_step(task, step)
                    if task.status == TaskStatus.FAILED:
                        return ToolResponse(
                            content=[{
                                "error": task.error,
                                "step": step.id
                            }],
                            isError=True
                        )
            except Exception as e:
                return ToolResponse(
                    content=[{
                        "error": str(e)
                    }],
                    isError=True
                )
            
            return ToolResponse(
                content=[{
                    "task_id": task.id,
                    "results": [step.result for step in task.steps if step.result],
                    "completed_at": task.completed_at.isoformat()
                }]
            )

        @self.app.post("/tools/create-adr")
        async def create_adr(request: ToolRequest) -> ToolResponse:
            title = request.arguments.get("title", "")
            context = request.arguments.get("context", {})
            options = request.arguments.get("options", [])
            decision = request.arguments.get("decision", "")
            """Create new ADR with analysis."""
            try:
                if not title.strip():
                    return ToolResponse(
                        content=[{
                            "error": "Title cannot be empty"
                        }],
                        isError=True
                    )
                if not decision.strip():
                    return ToolResponse(
                        content=[{
                            "error": "Decision cannot be empty"
                        }],
                        isError=True
                    )

                task = await self.task_manager.create_task(
                    type=TaskType.ADR_CREATION,
                    title=f"ADR: {title}",
                    description=f"Create ADR for {title}",
                    priority=TaskPriority.HIGH,
                    context={
                        "title": title,
                        "context": context,
                        "options": options,
                        "decision": decision
                    }
                )
                
                for step in task.steps:
                    task = await self.task_manager.execute_step(task, step)
                    if task.status == TaskStatus.FAILED:
                        return ToolResponse(
                            content=[{
                                "error": task.error,
                                "step": step.id
                            }],
                            isError=True
                        )
            except Exception as e:
                return ToolResponse(
                    content=[{
                        "error": str(e)
                    }],
                    isError=True
                )
            
            return ToolResponse(
                content=[{
                    "task_id": task.id,
                    "adr_path": task.context.get("adr_path"),
                    "completed_at": task.completed_at.isoformat()
                }]
            )

        @self.app.post("/tools/debug-issue")
        async def debug_issue(request: ToolRequest) -> ToolResponse:
            description = request.arguments.get("description", "")
            issue_type = request.arguments.get("type", "")
            context = request.arguments.get("context", {})
            """Debug issue systematically."""
            if not description.strip():
                return ToolResponse(
                    content=[{
                        "error": "Description cannot be empty"
                    }],
                    isError=True
                )
            try:
                task = await self.task_manager.create_task(
                    type=TaskType.DEBUG,
                    title=f"Debug: {description[:50]}...",
                    description=description,
                    priority=TaskPriority.HIGH,
                    context={
                        "issue_type": type,
                        "context": context
                    }
                )
                
                for step in task.steps:
                    task = await self.task_manager.execute_step(task, step)
                    if task.status == TaskStatus.FAILED:
                        return ToolResponse(
                            content=[{
                                "error": task.error,
                                "step": step.id
                            }],
                            isError=True
                        )
            except Exception as e:
                return ToolResponse(
                    content=[{
                        "error": str(e)
                    }],
                    isError=True
                )
            
            return ToolResponse(
                content=[{
                    "task_id": task.id,
                    "steps": [
                        {
                            "description": step.description,
                            "result": step.result
                        }
                        for step in task.steps if step.result
                    ],
                    "completed_at": task.completed_at.isoformat()
                }]
            )

        @self.app.post("/tools/crawl-docs")
        async def crawl_docs(request: ToolRequest) -> ToolResponse:
            urls = request.arguments.get("urls", [])
            source_type = request.arguments.get("source_type", "")
            """Crawl and store documentation."""
            if not urls:
                return ToolResponse(
                    content=[{
                        "error": "URLs list cannot be empty"
                    }],
                    isError=True
                )
            if not source_type.strip():
                return ToolResponse(
                    content=[{
                        "error": "Source type cannot be empty"
                    }],
                    isError=True
                )
            try:
                task = await self.task_manager.create_task(
                    type=TaskType.DOCUMENTATION,
                    title=f"Documentation: {source_type}",
                    description=f"Crawl and store {source_type} documentation",
                    priority=TaskPriority.MEDIUM,
                    context={
                        "urls": urls,
                        "source_type": source_type
                    }
                )
                
                for step in task.steps:
                    task = await self.task_manager.execute_step(task, step)
                    if task.status == TaskStatus.FAILED:
                        return ToolResponse(
                            content=[{
                                "error": task.error,
                                "step": step.id
                            }],
                            isError=True
                        )
            except Exception as e:
                return ToolResponse(
                    content=[{
                        "error": str(e)
                    }],
                    isError=True
                )
            
            return ToolResponse(
                content=[{
                    "task_id": task.id,
                    "docs_stored": task.context.get("docs_stored", []),
                    "completed_at": task.completed_at.isoformat()
                }]
            )

        @self.app.post("/tools/search-knowledge")
        async def search_knowledge(request: ToolRequest) -> ToolResponse:
            query = request.arguments.get("query", "")
            pattern_type = request.arguments.get("type")
            limit = request.arguments.get("limit", 5)
            """Search knowledge base for patterns and solutions."""
            if not query.strip():
                return ToolResponse(
                    content=[{
                        "error": "Search query cannot be empty"
                    }],
                    isError=True
                )
            try:
                pattern_type = PatternType(pattern_type) if pattern_type else None
                patterns = await self.knowledge_base.find_similar_patterns(
                    text=query,
                    type=pattern_type,
                    limit=limit
                )
            except Exception as e:
                return ToolResponse(
                    content=[{
                        "error": str(e)
                    }],
                    isError=True
                )
            
            return ToolResponse(
                content=[{
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "type": p.type.value,
                    "confidence": p.confidence.value,
                    "similarity": getattr(p, "similarity_score", None)
                } for p in patterns]
            )

        @self.app.post("/tools/get-task")
        async def get_task(request: ToolRequest) -> ToolResponse:
            task_id = request.arguments.get("task_id", "")
            """Get task status and results."""
            if not task_id.strip():
                return ToolResponse(
                    content=[{
                        "error": "Task ID cannot be empty"
                    }],
                    isError=True
                )
            try:
                task = await self.task_manager.get_task(task_id)
                if not task:
                    return ToolResponse(
                        content=[{
                            "error": f"Task not found: {task_id}"
                        }],
                        isError=True
                    )
            except Exception as e:
                return ToolResponse(
                    content=[{
                        "error": str(e)
                    }],
                    isError=True
                )
            
            return ToolResponse(
                content=[{
                    "id": task.id,
                    "type": task.type.value,
                    "title": task.title,
                    "status": task.status.value,
                    "steps": [
                        {
                            "id": step.id,
                            "description": step.description,
                            "status": step.status.value,
                            "result": step.result,
                            "error": step.error,
                            "completed_at": step.completed_at.isoformat() if step.completed_at else None
                        }
                        for step in task.steps
                    ],
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error": task.error
                }]
            )

    def start(self, host: str = "127.0.0.1", port: int = 3000):
        """Start the FastAPI server."""
        import uvicorn
        logger.info("Starting Codebase Analysis Server...")
        uvicorn.run(self.app, host=host, port=port)
        logger.info("Server started successfully")

    async def stop(self):
        """Stop the FastAPI server."""
        logger.info("Stopping Codebase Analysis Server...")
        # FastAPI will handle shutdown
        logger.info("Server stopped successfully")
