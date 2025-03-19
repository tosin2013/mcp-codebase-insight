from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
import uuid

from .config import ServerConfig
from .adr import ADRManager, ADRStatus
from .debug import DebugSystem, IssueType, IssueStatus
from .documentation import DocumentationManager
from .knowledge import KnowledgeBase, PatternType
from .prompts import PromptManager, PromptType, PromptContext
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TaskType(Enum):
    """Type of task."""
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE_REVIEW = "architecture_review"
    DEBUG = "debug"
    ADR_CREATION = "adr_creation"
    TEST_PLANNING = "test_planning"
    DOCUMENTATION = "documentation"

class TaskStatus(Enum):
    """Status of task."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(Enum):
    """Priority of task."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TaskStep:
    """Step in task execution."""
    id: str
    description: str
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

@dataclass
class Task:
    """Task for analysis or execution."""
    id: str
    type: TaskType
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    steps: List[TaskStep]
    context: Dict
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    related_tasks: List[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "steps": [step.to_dict() for step in self.steps],
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "related_tasks": self.related_tasks or []
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=TaskType(data["type"]),
            title=data["title"],
            description=data["description"],
            priority=TaskPriority(data["priority"]),
            status=TaskStatus(data["status"]),
            steps=[
                TaskStep(
                    id=step["id"],
                    description=step["description"],
                    status=TaskStatus(step["status"]),
                    result=step.get("result"),
                    error=step.get("error"),
                    started_at=datetime.fromisoformat(step["started_at"]) if step.get("started_at") else None,
                    completed_at=datetime.fromisoformat(step["completed_at"]) if step.get("completed_at") else None
                )
                for step in data["steps"]
            ],
            context=data["context"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error=data.get("error"),
            related_tasks=data.get("related_tasks", [])
        )

class TaskManager:
    """Manages task creation, tracking, and execution."""

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
        
        # Initialize task storage
        self.storage_dir = config.kb_storage_dir / "tasks"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize index
        self.index_path = self.storage_dir / "index.json"
        if not self.index_path.exists():
            self.index_path.write_text("{}")

    async def create_task(
        self,
        type: TaskType,
        title: str,
        description: str,
        priority: TaskPriority,
        context: Dict
    ) -> Task:
        """Create new task."""
        # Generate unique ID
        task_id = str(uuid.uuid4())
        
        # Create initial steps based on task type
        steps = await self._create_task_steps(type, context)
        
        # Create task
        task = Task(
            id=task_id,
            type=type,
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.NEW,
            steps=steps,
            context=context,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save task
        await self._save_task(task)
        
        return task

    async def execute_step(
        self,
        task: Task,
        step: TaskStep
    ) -> Task:
        """Execute task step."""
        step.started_at = datetime.now()
        step.status = TaskStatus.IN_PROGRESS
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.now()
        
        try:
            # Execute step based on task type
            if task.type == TaskType.CODE_ANALYSIS:
                result = await self._execute_analysis_step(task, step)
            elif task.type == TaskType.ARCHITECTURE_REVIEW:
                result = await self._execute_architecture_step(task, step)
            elif task.type == TaskType.DEBUG:
                result = await self._execute_debug_step(task, step)
            elif task.type == TaskType.ADR_CREATION:
                result = await self._execute_adr_step(task, step)
            elif task.type == TaskType.TEST_PLANNING:
                result = await self._execute_test_step(task, step)
            elif task.type == TaskType.DOCUMENTATION:
                result = await self._execute_documentation_step(task, step)
            else:
                raise ValueError(f"Unknown task type: {task.type}")
            
            step.result = result
            step.status = TaskStatus.COMPLETED
            
        except Exception as e:
            step.error = str(e)
            step.status = TaskStatus.FAILED
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Error executing step {step.id} of task {task.id}: {e}")
        
        step.completed_at = datetime.now()
        task.updated_at = datetime.now()
        
        # Check if all steps are completed
        if all(s.status == TaskStatus.COMPLETED for s in task.steps):
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
        
        # Save updated task
        await self._save_task(task)
        
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        task_path = self.storage_dir / f"{task_id}.json"
        if not task_path.exists():
            return None
        
        data = json.loads(task_path.read_text())
        return Task.from_dict(data)

    async def list_tasks(
        self,
        type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """List tasks with optional filters."""
        tasks = []
        for task_file in self.storage_dir.glob("*.json"):
            data = json.loads(task_file.read_text())
            task = Task.from_dict(data)
            
            if type and task.type != type:
                continue
            if status and task.status != status:
                continue
            if priority and task.priority != priority:
                continue
            
            tasks.append(task)
        
        return sorted(tasks, key=lambda t: t.updated_at, reverse=True)

    async def _create_task_steps(self, type: TaskType, context: Dict) -> List[TaskStep]:
        """Create steps for task type."""
        steps = []
        
        if type == TaskType.CODE_ANALYSIS:
            steps = [
                TaskStep(id="analyze", description="Analyze code patterns", status=TaskStatus.NEW),
                TaskStep(id="suggest", description="Generate suggestions", status=TaskStatus.NEW)
            ]
        elif type == TaskType.ARCHITECTURE_REVIEW:
            steps = [
                TaskStep(id="review", description="Review architecture", status=TaskStatus.NEW),
                TaskStep(id="evaluate", description="Evaluate design patterns", status=TaskStatus.NEW),
                TaskStep(id="recommend", description="Provide recommendations", status=TaskStatus.NEW)
            ]
        elif type == TaskType.DEBUG:
            steps = [
                TaskStep(id="understand", description="Understand the system", status=TaskStatus.NEW),
                TaskStep(id="reproduce", description="Reproduce the issue", status=TaskStatus.NEW),
                TaskStep(id="analyze", description="Analyze root cause", status=TaskStatus.NEW),
                TaskStep(id="fix", description="Implement fix", status=TaskStatus.NEW),
                TaskStep(id="verify", description="Verify solution", status=TaskStatus.NEW)
            ]
        elif type == TaskType.ADR_CREATION:
            steps = [
                TaskStep(id="context", description="Gather context", status=TaskStatus.NEW),
                TaskStep(id="options", description="Analyze options", status=TaskStatus.NEW),
                TaskStep(id="decide", description="Make decision", status=TaskStatus.NEW),
                TaskStep(id="document", description="Document ADR", status=TaskStatus.NEW)
            ]
        elif type == TaskType.TEST_PLANNING:
            steps = [
                TaskStep(id="analyze", description="Analyze requirements", status=TaskStatus.NEW),
                TaskStep(id="design", description="Design test cases", status=TaskStatus.NEW),
                TaskStep(id="plan", description="Create test plan", status=TaskStatus.NEW)
            ]
        elif type == TaskType.DOCUMENTATION:
            steps = [
                TaskStep(id="gather", description="Gather information", status=TaskStatus.NEW),
                TaskStep(id="structure", description="Structure documentation", status=TaskStatus.NEW),
                TaskStep(id="write", description="Write documentation", status=TaskStatus.NEW),
                TaskStep(id="review", description="Review and finalize", status=TaskStatus.NEW)
            ]
        
        return steps

    async def _save_task(self, task: Task) -> None:
        """Save task to file."""
        task_path = self.storage_dir / f"{task.id}.json"
        task_path.write_text(json.dumps(task.to_dict(), indent=2))
        
        # Update index
        index = json.loads(self.index_path.read_text())
        index[task.id] = {
            "type": task.type.value,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "updated_at": task.updated_at.isoformat()
        }
        self.index_path.write_text(json.dumps(index, indent=2))

    # Step execution methods would be implemented here
    # Each would use the appropriate managers (ADR, Debug, etc.)
    # and coordinate between them to complete the step
    async def _execute_analysis_step(self, task: Task, step: TaskStep) -> str:
        """Execute code analysis step."""
        # Implementation would use knowledge base and prompt manager
        pass

    async def _execute_architecture_step(self, task: Task, step: TaskStep) -> str:
        """Execute architecture review step."""
        # Implementation would use knowledge base and ADR manager
        pass

    async def _execute_debug_step(self, task: Task, step: TaskStep) -> str:
        """Execute debug step."""
        # Implementation would use debug system
        pass

    async def _execute_adr_step(self, task: Task, step: TaskStep) -> str:
        """Execute ADR creation step."""
        # Implementation would use ADR manager
        pass

    async def _execute_test_step(self, task: Task, step: TaskStep) -> str:
        """Execute test planning step."""
        # Implementation would use knowledge base and prompt manager
        pass

    async def _execute_documentation_step(self, task: Task, step: TaskStep) -> str:
        """Execute documentation step."""
        # Implementation would use documentation manager
        pass
