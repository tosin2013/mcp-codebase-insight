"""Task management module."""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import json
from pathlib import Path

from pydantic import BaseModel

class TaskType(str, Enum):
    """Task type enumeration."""
    
    CODE_ANALYSIS = "code_analysis"
    PATTERN_EXTRACTION = "pattern_extraction"
    DOCUMENTATION = "documentation"
    DOCUMENTATION_CRAWL = "doc_crawl"
    DEBUG = "debug"
    ADR = "adr"

class TaskStatus(str, Enum):
    """Task status enumeration."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Task priority enumeration."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Task(BaseModel):
    """Task model."""
    
    id: UUID
    type: TaskType
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    context: Dict
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None

class TaskManager:
    """Manager for asynchronous tasks."""
    
    def __init__(
        self,
        config,
        adr_manager=None,
        debug_system=None,
        doc_manager=None,
        knowledge_base=None,
        prompt_manager=None
    ):
        """Initialize task manager."""
        self.config = config
        self.adr_manager = adr_manager
        self.debug_system = debug_system
        self.doc_manager = doc_manager
        self.kb = knowledge_base
        self.prompt_manager = prompt_manager
        
        # Initialize tasks directory
        self.tasks_dir = Path(config.docs_cache_dir) / "tasks"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks: Dict[UUID, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
    
    async def start(self):
        """Start task processing."""
        self.running = True
        asyncio.create_task(self._process_tasks())
    
    async def stop(self):
        """Stop task processing."""
        self.running = False
        # Wait for queue to be empty
        if not self.task_queue.empty():
            await self.task_queue.join()
    
    async def _save_task(self, task: Task):
        """Save task to disk."""
        task_path = self.tasks_dir / f"{task.id}.json"
        with open(task_path, "w") as f:
            json.dump(task.model_dump(), f, indent=2, default=str)

    async def create_task(
        self,
        type: str,
        title: str,
        description: str,
        context: Dict,
        priority: TaskPriority = TaskPriority.MEDIUM,
        metadata: Optional[Dict[str, str]] = None
    ) -> Task:
        """Create a new task."""
        now = datetime.utcnow()
        task = Task(
            id=uuid4(),
            type=TaskType(type),
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            context=context,
            metadata=metadata,
            created_at=now,
            updated_at=now
        )
        
        self.tasks[task.id] = task
        await self._save_task(task)  # Save task to disk
        await self.task_queue.put(task)
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        task_path = self.tasks_dir / f"{task_id}.json"
        if not task_path.exists():
            return None
            
        with open(task_path) as f:
            data = json.load(f)
            return Task(**data)
    
    async def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> Optional[Task]:
        """Update task status and result."""
        task = await self.get_task(task_id)
        if not task:
            return None
            
        if status:
            task.status = status
        if result:
            task.result = result
        if error:
            task.error = error
            
        task.updated_at = datetime.utcnow()
        if status == "completed":
            task.completed_at = datetime.utcnow()
            
        await self._save_task(task)
        return task
    
    async def cancel_task(self, task_id: UUID) -> Optional[Task]:
        """Cancel a pending or in-progress task."""
        task = self.tasks.get(task_id)
        if not task:
            return None
            
        if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.utcnow()
            
        return task
    
    async def list_tasks(
        self,
        type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """List all tasks, optionally filtered."""
        tasks = []
        for task in self.tasks.values():
            if type and task.type != type:
                continue
            if status and task.status != status:
                continue
            if priority and task.priority != priority:
                continue
            tasks.append(task)
            
        return sorted(tasks, key=lambda x: x.created_at)
    
    async def _process_tasks(self):
        """Process tasks from queue."""
        while self.running:
            try:
                task = await self.task_queue.get()
                
                # Update status
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = datetime.utcnow()
                
                try:
                    # Process task based on type
                    if task.type == TaskType.CODE_ANALYSIS:
                        result = await self._analyze_code(task)
                    elif task.type == TaskType.PATTERN_EXTRACTION:
                        result = await self._extract_patterns(task)
                    elif task.type == TaskType.DOCUMENTATION:
                        result = await self._generate_documentation(task)
                    elif task.type == TaskType.DOCUMENTATION_CRAWL:
                        result = await self._crawl_documentation(task)
                    elif task.type == TaskType.DEBUG:
                        result = await self._debug_issue(task)
                    elif task.type == TaskType.ADR:
                        result = await self._process_adr(task)
                    else:
                        raise ValueError(f"Unknown task type: {task.type}")
                        
                    # Update task with result
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    
                except Exception as e:
                    # Update task with error
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                    
                task.completed_at = datetime.utcnow()
                task.updated_at = datetime.utcnow()
                
            except asyncio.CancelledError:
                break
                
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing task: {e}")
                
            finally:
                self.task_queue.task_done()
    
    async def _analyze_code(self, task: Task) -> Dict:
        """Analyze code and extract insights."""
        if not self.kb:
            raise ValueError("Knowledge base not available")
            
        code = task.context.get("code")
        if not code:
            raise ValueError("No code provided for analysis")
            
        # Find similar patterns
        patterns = await self.kb.find_similar_patterns(
            query=code,
            limit=5
        )
        
        return {
            "patterns": [p.dict() for p in patterns],
            "insights": [
                p.pattern.description for p in patterns
            ]
        }
    
    async def _extract_patterns(self, task: Task) -> Dict:
        """Extract patterns from code."""
        if not self.kb:
            raise ValueError("Knowledge base not available")
            
        code = task.context.get("code")
        if not code:
            raise ValueError("No code provided for pattern extraction")
            
        # TODO: Implement pattern extraction logic
        return {
            "patterns": []
        }
    
    async def _generate_documentation(self, task: Task) -> Dict:
        """Generate documentation."""
        if not self.doc_manager:
            raise ValueError("Documentation manager not available")
            
        content = task.context.get("content")
        if not content:
            raise ValueError("No content provided for documentation")
            
        doc = await self.doc_manager.add_document(
            title=task.title,
            content=content,
            type="documentation",
            metadata=task.metadata
        )
        
        return {
            "document_id": str(doc.id),
            "path": f"docs/{doc.id}.json"
        }
    
    async def _crawl_documentation(self, task: Task) -> Dict:
        """Crawl documentation from URLs."""
        if not self.doc_manager:
            raise ValueError("Documentation manager not available")
            
        urls = task.context.get("urls")
        source_type = task.context.get("source_type")
        if not urls or not source_type:
            raise ValueError("Missing required fields: urls, source_type")
            
        docs = await self.doc_manager.crawl_docs(
            urls=urls,
            source_type=source_type
        )
        
        return {
            "documents": [doc.model_dump() for doc in docs],
            "total_documents": len(docs)
        }
    
    async def _debug_issue(self, task: Task) -> Dict:
        """Debug an issue."""
        if not self.debug_system:
            raise ValueError("Debug system not available")
            
        issue = await self.debug_system.create_issue(
            title=task.title,
            type="bug",
            description=task.context
        )
        
        steps = await self.debug_system.analyze_issue(issue.id)
        
        return {
            "issue_id": str(issue.id),
            "steps": steps
        }
    
    async def _process_adr(self, task: Task) -> Dict:
        """Process ADR-related task."""
        if not self.adr_manager:
            raise ValueError("ADR manager not available")
            
        adr = await self.adr_manager.create_adr(
            title=task.title,
            context=task.context.get("context", {}),
            options=task.context.get("options", []),
            decision=task.context.get("decision", "")
        )
        
        return {
            "adr_id": str(adr.id),
            "path": f"docs/adrs/{adr.id}.json"
        }
