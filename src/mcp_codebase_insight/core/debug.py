"""Debug system for issue tracking and analysis."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

class IssueType(str, Enum):
    """Issue type enumeration."""
    
    BUG = "bug"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DESIGN = "design"
    DOCUMENTATION = "documentation"
    OTHER = "other"

class IssueStatus(str, Enum):
    """Issue status enumeration."""
    
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    WONT_FIX = "wont_fix"

class Issue(BaseModel):
    """Issue model."""
    
    id: UUID
    title: str
    type: IssueType
    status: IssueStatus
    description: Dict
    steps: Optional[List[Dict]] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None

class DebugSystem:
    """System for debugging and issue management."""
    
    def __init__(self, config):
        """Initialize debug system."""
        self.config = config
        self.debug_dir = Path(config.docs_cache_dir) / "debug"
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        self.issues: Dict[UUID, Issue] = {}
        self.initialized = False
        
    async def initialize(self) -> None:
        """Initialize debug system."""
        if self.initialized:
            return
            
        try:
            # Load existing issues
            if self.debug_dir.exists():
                for issue_file in self.debug_dir.glob("*.json"):
                    try:
                        with open(issue_file) as f:
                            data = json.load(f)
                            issue = Issue(**data)
                            self.issues[issue.id] = issue
                    except Exception as e:
                        # Log error but continue loading other issues
                        print(f"Error loading issue {issue_file}: {e}")
            
            self.initialized = True
        except Exception as e:
            print(f"Error initializing debug system: {e}")
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize debug system: {str(e)}")
                    
    async def cleanup(self) -> None:
        """Clean up debug system resources."""
        if not self.initialized:
            return
            
        try:
            # Save any pending issues
            for issue in self.issues.values():
                try:
                    await self._save_issue(issue)
                except Exception as e:
                    print(f"Error saving issue {issue.id}: {e}")
            # Clear in-memory issues
            self.issues.clear()
        except Exception as e:
            print(f"Error cleaning up debug system: {e}")
        finally:
            self.initialized = False
    
    async def create_issue(
        self,
        title: str,
        type: str,
        description: Dict
    ) -> Issue:
        """Create a new issue."""
        now = datetime.utcnow()
        issue = Issue(
            id=uuid4(),
            title=title,
            type=IssueType(type),
            status=IssueStatus.OPEN,
            description=description,
            created_at=now,
            updated_at=now
        )
        
        await self._save_issue(issue)
        return issue
    
    async def get_issue(self, issue_id: UUID) -> Optional[Issue]:
        """Get issue by ID."""
        issue_path = self.debug_dir / f"{issue_id}.json"
        if not issue_path.exists():
            return None
            
        with open(issue_path) as f:
            data = json.load(f)
            return Issue(**data)
    
    async def update_issue(
        self,
        issue_id: UUID,
        status: Optional[IssueStatus] = None,
        steps: Optional[List[Dict]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[Issue]:
        """Update issue status and details."""
        issue = await self.get_issue(issue_id)
        if not issue:
            return None
            
        if status:
            issue.status = status
            if status == IssueStatus.RESOLVED:
                issue.resolved_at = datetime.utcnow()
        if steps:
            issue.steps = steps
        if metadata:
            issue.metadata = {**(issue.metadata or {}), **metadata}
            
        issue.updated_at = datetime.utcnow()
        await self._save_issue(issue)
        return issue
    
    async def list_issues(
        self,
        type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None
    ) -> List[Issue]:
        """List all issues, optionally filtered by type and status."""
        issues = []
        for path in self.debug_dir.glob("*.json"):
            with open(path) as f:
                data = json.load(f)
                issue = Issue(**data)
                if (not type or issue.type == type) and (not status or issue.status == status):
                    issues.append(issue)
        return sorted(issues, key=lambda x: x.created_at)
    
    async def analyze_issue(self, issue_id: UUID) -> List[Dict]:
        """Analyze issue and generate debug steps."""
        issue = await self.get_issue(issue_id)
        if not issue:
            return []
            
        # Generate analysis steps based on issue type
        steps = []
        
        if issue.type == IssueType.BUG:
            steps.extend([
                {"type": "check", "name": "Reproduce Issue", "description": "Steps to reproduce the issue"},
                {"type": "check", "name": "Error Logs", "description": "Check relevant error logs"},
                {"type": "check", "name": "Stack Trace", "description": "Analyze stack trace if available"},
                {"type": "check", "name": "Code Review", "description": "Review related code sections"}
            ])
            
        elif issue.type == IssueType.PERFORMANCE:
            steps.extend([
                {"type": "check", "name": "Profiling", "description": "Run performance profiling"},
                {"type": "check", "name": "Resource Usage", "description": "Monitor CPU, memory, I/O"},
                {"type": "check", "name": "Query Analysis", "description": "Review database queries"},
                {"type": "check", "name": "Bottlenecks", "description": "Identify performance bottlenecks"}
            ])
            
        elif issue.type == IssueType.SECURITY:
            steps.extend([
                {"type": "check", "name": "Vulnerability Scan", "description": "Run security scanners"},
                {"type": "check", "name": "Access Control", "description": "Review permissions"},
                {"type": "check", "name": "Input Validation", "description": "Check input handling"},
                {"type": "check", "name": "Dependencies", "description": "Audit dependencies"}
            ])
            
        # Update issue with analysis steps
        await self.update_issue(issue_id, steps=steps)
        return steps
    
    async def _save_issue(self, issue: Issue) -> None:
        """Save issue to file."""
        issue_path = self.debug_dir / f"{issue.id}.json"
        with open(issue_path, "w") as f:
            json.dump(issue.model_dump(), f, indent=2, default=str)
