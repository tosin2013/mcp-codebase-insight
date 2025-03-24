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
        self._process_task_future = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize task manager and start processing tasks."""
        if self.initialized:
            return
            
        try:
            # Create a fresh queue
            self.task_queue = asyncio.Queue()
            
            # Load existing tasks from disk
            if self.tasks_dir.exists():
                for task_file in self.tasks_dir.glob("*.json"):
                    try:
                        with open(task_file) as f:
                            data = json.load(f)
                            task = Task(**data)
                            self.tasks[task.id] = task
                    except Exception as e:
                        print(f"Error loading task {task_file}: {e}")
            
            # Start task processing
            await self.start()
            self.initialized = True
        except Exception as e:
            print(f"Error initializing task manager: {e}")
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize task manager: {str(e)}")
    
    async def cleanup(self):
        """Clean up task manager and stop processing tasks."""
        if not self.initialized:
            return
            
        try:
            # Stop task processing
            await self.stop()
            
            # Save any remaining tasks
            for task in self.tasks.values():
                if task.status == TaskStatus.IN_PROGRESS:
                    task.status = TaskStatus.FAILED
                    task.error = "Server shutdown"
                    task.updated_at = datetime.utcnow()
                    await self._save_task(task)
        except Exception as e:
            print(f"Error cleaning up task manager: {e}")
        finally:
            self.initialized = False
    
    async def start(self):
        """Start task processing."""
        if not self.running:
            self.running = True
            self._process_task_future = asyncio.create_task(self._process_tasks())
    
    async def stop(self):
        """Stop task processing."""
        if self.running:
            self.running = False
            if self._process_task_future:
                try:
                    # Wait for the task to finish with a timeout
                    await asyncio.wait_for(self._process_task_future, timeout=5.0)
                except asyncio.TimeoutError:
                    # If it doesn't finish in time, cancel it
                    self._process_task_future.cancel()
                    try:
                        await self._process_task_future
                    except asyncio.CancelledError:
                        pass
                finally:
                    self._process_task_future = None

            # Create a new empty queue instead of trying to drain the old one
            # This avoids task_done() issues
            self.task_queue = asyncio.Queue()
    
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
                # Use get with timeout to avoid blocking forever
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Update status
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = datetime.utcnow()
                
                try:
                    # Process task based on type
                    if task.type == TaskType.CODE_ANALYSIS:
                        await self._process_code_analysis(task)
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
                
                # Mark task as done in the queue
                self.task_queue.task_done()
                
            except asyncio.CancelledError:
                # Don't call task_done() here since we didn't get a task
                break
                
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing task: {e}")
                # Don't call task_done() here since we might not have gotten a task
    
    async def _process_code_analysis(self, task: Task) -> None:
        """Process a code analysis task."""
        try:
            code = task.context.get("code", "")
            context = task.context.get("context", {})
            
            patterns = await self.app.state.knowledge.analyze_code(
                code=code,
                language=context.get("language", "python"),
                purpose=context.get("purpose", "")
            )
            
            await self._update_task(
                task,
                status=TaskStatus.COMPLETED,
                result={"patterns": [p.pattern.model_dump() for p in patterns]}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to process code analysis task: {str(e)}")
            await self._update_task(
                task,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
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

    async def _process_doc_crawl(self, task: Task) -> None:
        """Process a document crawl task."""
        try:
            urls = task.context.get("urls", [])
            source_type = task.context.get("source_type", "markdown")
            
            total_documents = 0
            for url in urls:
                try:
                    await self.doc_manager.crawl_document(url, source_type)
                    total_documents += 1
                except Exception as e:
                    print(f"Failed to crawl document {url}: {str(e)}")
            
            task.status = TaskStatus.COMPLETED
            task.result = {"total_documents": total_documents}
            task.updated_at = datetime.utcnow()
            task.completed_at = datetime.utcnow()
            await self._save_task(task)
            
        except Exception as e:
            print(f"Failed to process doc crawl task: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = datetime.utcnow()
            await self._save_task(task)
