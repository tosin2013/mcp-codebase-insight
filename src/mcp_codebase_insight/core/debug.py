"""Debugging and issue tracking."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.errors import TaskError
from mcp_codebase_insight.utils.logger import get_logger

logger = get_logger(__name__)

class IssueType(str, Enum):
    """Types of issues."""
    BUG = "bug"
    PERFORMANCE = "performance"
    SECURITY = "security"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"

class IssueStatus(str, Enum):
    """Issue status."""
    OPEN = "open"
    ANALYZING = "analyzing"
    ROOT_CAUSE_IDENTIFIED = "root_cause_identified"
    SOLUTION_PROPOSED = "solution_proposed"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IssuePriority(str, Enum):
    """Issue priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class DebugStep:
    """A step in the debugging process."""
    id: str
    description: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None

@dataclass
class Issue:
    """A tracked issue."""
    id: str
    title: str
    description: str
    type: IssueType
    status: IssueStatus
    priority: IssuePriority
    steps: List[DebugStep]
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    resolved_at: Optional[datetime] = None

class DebugSystem:
    """System for debugging and issue tracking."""

    def __init__(self, config: ServerConfig):
        """Initialize debug system."""
        self.config = config
        self.issues: Dict[str, Issue] = {}

    async def create_issue(
        self,
        title: str,
        description: str,
        type: IssueType,
        priority: IssuePriority,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Issue:
        """Create a new issue."""
        try:
            from uuid import uuid4
            issue_id = str(uuid4())
            
            # Create initial debug steps following Agans' 9 Rules
            steps = [
                DebugStep(
                    id="understand_system",
                    description="Understand the system's normal behavior"
                ),
                DebugStep(
                    id="make_it_fail",
                    description="Make it fail consistently"
                ),
                DebugStep(
                    id="maximize_output",
                    description="Maximize the output"
                ),
                DebugStep(
                    id="divide_and_conquer",
                    description="Divide and conquer"
                ),
                DebugStep(
                    id="change_one_thing",
                    description="Change one thing at a time"
                ),
                DebugStep(
                    id="keep_audit_trail",
                    description="Keep an audit trail"
                ),
                DebugStep(
                    id="check_plug",
                    description="Check the plug"
                ),
                DebugStep(
                    id="get_fresh_view",
                    description="Get a fresh view"
                ),
                DebugStep(
                    id="if_you_fixed_it",
                    description="If you did fix it, why did you fix it?"
                )
            ]
            
            issue = Issue(
                id=issue_id,
                title=title,
                description=description,
                type=type,
                status=IssueStatus.OPEN,
                priority=priority,
                steps=steps,
                metadata=metadata or {}
            )
            
            self.issues[issue_id] = issue
            logger.info(f"Created issue {issue_id}: {title}")
            
            return issue
        except Exception as e:
            raise TaskError(f"Failed to create issue: {e}")

    async def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue by ID."""
        return self.issues.get(issue_id)

    async def update_issue(
        self,
        issue_id: str,
        status: Optional[IssueStatus] = None,
        root_cause: Optional[str] = None,
        solution: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Issue:
        """Update an issue."""
        try:
            issue = self.issues.get(issue_id)
            if not issue:
                raise TaskError(f"Issue not found: {issue_id}")
            
            if status is not None:
                issue.status = status
                if status == IssueStatus.RESOLVED:
                    issue.resolved_at = datetime.utcnow()
            if root_cause is not None:
                issue.root_cause = root_cause
            if solution is not None:
                issue.solution = solution
            if metadata is not None:
                issue.metadata.update(metadata)
            
            issue.updated_at = datetime.utcnow()
            logger.info(f"Updated issue {issue_id}")
            
            return issue
        except Exception as e:
            raise TaskError(f"Failed to update issue: {e}")

    async def complete_step(
        self,
        issue_id: str,
        step_id: str,
        result: Dict[str, Any]
    ) -> Issue:
        """Complete a debug step."""
        try:
            issue = self.issues.get(issue_id)
            if not issue:
                raise TaskError(f"Issue not found: {issue_id}")
            
            step = next((s for s in issue.steps if s.id == step_id), None)
            if not step:
                raise TaskError(f"Step not found: {step_id}")
            
            step.result = result
            step.completed_at = datetime.utcnow()
            issue.updated_at = datetime.utcnow()
            
            logger.info(f"Completed step {step_id} for issue {issue_id}")
            return issue
        except Exception as e:
            raise TaskError(f"Failed to complete step: {e}")

    async def list_issues(
        self,
        type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
        priority: Optional[IssuePriority] = None
    ) -> List[Issue]:
        """List issues with optional filters."""
        issues = list(self.issues.values())
        
        if type:
            issues = [i for i in issues if i.type == type]
        if status:
            issues = [i for i in issues if i.status == status]
        if priority:
            issues = [i for i in issues if i.priority == priority]
        
        return sorted(issues, key=lambda i: i.updated_at, reverse=True)

    async def analyze_issue(
        self,
        issue_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze an issue using Agans' 9 Rules."""
        try:
            issue = self.issues.get(issue_id)
            if not issue:
                raise TaskError(f"Issue not found: {issue_id}")
            
            # Update status
            issue.status = IssueStatus.ANALYZING
            issue.updated_at = datetime.utcnow()
            
            # Analyze based on completed steps
            completed_steps = [s for s in issue.steps if s.completed_at]
            if not completed_steps:
                return {
                    "status": "incomplete",
                    "message": "No debug steps completed yet"
                }
            
            # Analyze patterns and insights
            insights = []
            for step in completed_steps:
                if step.result:
                    insights.append({
                        "step": step.id,
                        "description": step.description,
                        "findings": step.result
                    })
            
            return {
                "status": "analyzed",
                "issue_type": issue.type.value,
                "completed_steps": len(completed_steps),
                "total_steps": len(issue.steps),
                "insights": insights,
                "context": context or {}
            }
        except Exception as e:
            raise TaskError(f"Failed to analyze issue: {e}")
