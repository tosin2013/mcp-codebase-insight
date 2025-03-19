"""Task management and execution."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.adr import ADRManager
from mcp_codebase_insight.core.debug import DebugSystem
from mcp_codebase_insight.core.documentation import DocumentationManager
from mcp_codebase_insight.core.knowledge import KnowledgeBase
from mcp_codebase_insight.core.prompts import PromptManager
from mcp_codebase_insight.core.errors import TaskError
from mcp_codebase_insight.utils.logger import get_logger

logger = get_logger(__name__)

class TaskType(str, Enum):
    """Types of tasks."""
    CODE_ANALYSIS = "code_analysis"
    ADR_CREATION = "adr_creation"
    DEBUG = "debug"
    DOCUMENTATION = "documentation"
    KNOWLEDGE_BASE = "knowledge_base"

class TaskPriority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class TaskStep:
    """A single step in a task."""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class Task:
    """A task to be executed."""
    id: str
    type: TaskType
    title: str
    description: str
    priority: TaskPriority
    context: Dict[str, Any]
    steps: List[TaskStep]
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskManager:
    """Manager for task execution and tracking."""

    def __init__(
        self,
        config: ServerConfig,
        adr_manager: ADRManager,
        debug_system: DebugSystem,
        doc_manager: DocumentationManager,
        knowledge_base: KnowledgeBase,
        prompt_manager: PromptManager
    ):
        """Initialize task manager."""
        self.config = config
        self.adr_manager = adr_manager
        self.debug_system = debug_system
        self.doc_manager = doc_manager
        self.knowledge_base = knowledge_base
        self.prompt_manager = prompt_manager
        self.tasks: Dict[str, Task] = {}

    async def create_task(
        self,
        type: TaskType,
        title: str,
        description: str,
        priority: TaskPriority,
        context: Dict[str, Any]
    ) -> Task:
        """Create a new task."""
        try:
            task_id = str(uuid4())
            steps = self._create_steps(type, context)
            
            task = Task(
                id=task_id,
                type=type,
                title=title,
                description=description,
                priority=priority,
                context=context,
                steps=steps
            )
            
            self.tasks[task_id] = task
            logger.info(f"Created task {task_id}: {title}")
            
            return task
        except Exception as e:
            raise TaskError(f"Failed to create task: {e}")

    def _create_steps(self, type: TaskType, context: Dict[str, Any]) -> List[TaskStep]:
        """Create steps for a task type."""
        steps = []
        
        if type == TaskType.CODE_ANALYSIS:
            steps = [
                TaskStep(
                    id="analyze_patterns",
                    description="Analyze code patterns and structure"
                ),
                TaskStep(
                    id="check_best_practices",
                    description="Check adherence to best practices"
                ),
                TaskStep(
                    id="identify_improvements",
                    description="Identify potential improvements"
                )
            ]
        elif type == TaskType.ADR_CREATION:
            steps = [
                TaskStep(
                    id="analyze_context",
                    description="Analyze decision context"
                ),
                TaskStep(
                    id="evaluate_options",
                    description="Evaluate decision options"
                ),
                TaskStep(
                    id="document_decision",
                    description="Document final decision"
                )
            ]
        elif type == TaskType.DEBUG:
            steps = [
                TaskStep(
                    id="analyze_issue",
                    description="Analyze issue description"
                ),
                TaskStep(
                    id="identify_cause",
                    description="Identify root cause"
                ),
                TaskStep(
                    id="propose_solution",
                    description="Propose solution"
                )
            ]
        elif type == TaskType.DOCUMENTATION:
            steps = [
                TaskStep(
                    id="crawl_docs",
                    description="Crawl documentation sources"
                ),
                TaskStep(
                    id="process_content",
                    description="Process and structure content"
                ),
                TaskStep(
                    id="store_docs",
                    description="Store documentation"
                )
            ]
        elif type == TaskType.KNOWLEDGE_BASE:
            steps = [
                TaskStep(
                    id="extract_patterns",
                    description="Extract knowledge patterns"
                ),
                TaskStep(
                    id="validate_patterns",
                    description="Validate patterns"
                ),
                TaskStep(
                    id="store_patterns",
                    description="Store patterns in knowledge base"
                )
            ]
        else:
            raise TaskError(f"Unknown task type: {type}")
        
        return steps

    async def execute_step(self, task: Task, step: TaskStep) -> Task:
        """Execute a task step."""
        try:
            step.status = TaskStatus.RUNNING
            step.started_at = datetime.utcnow()
            task.status = TaskStatus.RUNNING
            task.started_at = task.started_at or datetime.utcnow()
            task.updated_at = datetime.utcnow()
            
            logger.info(f"Executing step {step.id} for task {task.id}")
            
            # Execute step based on task type
            if task.type == TaskType.CODE_ANALYSIS:
                await self._execute_code_analysis_step(task, step)
            elif task.type == TaskType.ADR_CREATION:
                await self._execute_adr_creation_step(task, step)
            elif task.type == TaskType.DEBUG:
                await self._execute_debug_step(task, step)
            elif task.type == TaskType.DOCUMENTATION:
                await self._execute_documentation_step(task, step)
            elif task.type == TaskType.KNOWLEDGE_BASE:
                await self._execute_knowledge_base_step(task, step)
            else:
                raise TaskError(f"Unknown task type: {task.type}")
            
            step.status = TaskStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            
            # Check if all steps are completed
            if all(s.status == TaskStatus.COMPLETED for s in task.steps):
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
            
            task.updated_at = datetime.utcnow()
            return task
        except Exception as e:
            step.status = TaskStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = datetime.utcnow()
            logger.error(f"Failed to execute step {step.id} for task {task.id}: {e}")
            return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    async def list_tasks(
        self,
        type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """List tasks with optional filters."""
        tasks = list(self.tasks.values())
        
        if type:
            tasks = [t for t in tasks if t.type == type]
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    async def _execute_code_analysis_step(self, task: Task, step: TaskStep):
        """Execute code analysis step."""
        if step.id == "analyze_patterns":
            # Analyze code patterns
            pass
        elif step.id == "check_best_practices":
            # Check best practices
            pass
        elif step.id == "identify_improvements":
            # Identify improvements
            pass

    async def _execute_adr_creation_step(self, task: Task, step: TaskStep):
        """Execute ADR creation step."""
        if step.id == "analyze_context":
            # Analyze context
            pass
        elif step.id == "evaluate_options":
            # Evaluate options
            pass
        elif step.id == "document_decision":
            # Document decision
            pass

    async def _execute_debug_step(self, task: Task, step: TaskStep):
        """Execute debug step."""
        if step.id == "analyze_issue":
            # Analyze issue
            pass
        elif step.id == "identify_cause":
            # Identify cause
            pass
        elif step.id == "propose_solution":
            # Propose solution
            pass

    async def _execute_documentation_step(self, task: Task, step: TaskStep):
        """Execute documentation step."""
        if step.id == "crawl_docs":
            # Crawl docs
            pass
        elif step.id == "process_content":
            # Process content
            pass
        elif step.id == "store_docs":
            # Store docs
            pass

    async def _execute_knowledge_base_step(self, task: Task, step: TaskStep):
        """Execute knowledge base step."""
        if step.id == "extract_patterns":
            # Extract patterns
            pass
        elif step.id == "validate_patterns":
            # Validate patterns
            pass
        elif step.id == "store_patterns":
            # Store patterns
            pass
