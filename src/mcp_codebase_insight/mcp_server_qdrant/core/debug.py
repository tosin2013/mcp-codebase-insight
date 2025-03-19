from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import json
import structlog
from git import Repo

from .config import ServerConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class IssueStatus(Enum):
    """Status of a debug issue."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    REOPENED = "reopened"

class IssueType(Enum):
    """Type of debug issue."""
    BUG = "bug"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    INTEGRATION = "integration"

@dataclass
class Observation:
    """Observed behavior during debugging."""
    timestamp: datetime
    description: str
    data: Dict
    context: Dict
    source: str

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "data": self.data,
            "context": self.context,
            "source": self.source
        }

@dataclass
class DebugStep:
    """Step in the debugging process."""
    rule: str  # Which of Agans' rules this step follows
    action: str
    result: str
    observations: List[Observation]
    timestamp: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "rule": self.rule,
            "action": self.action,
            "result": self.result,
            "observations": [obs.to_dict() for obs in self.observations],
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class DebugSession:
    """Debugging session following Agans' 9 Rules."""
    issue_id: str
    issue_type: IssueType
    status: IssueStatus
    description: str
    steps: List[DebugStep]
    system_context: Dict
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "issue_id": self.issue_id,
            "issue_type": self.issue_type.value,
            "status": self.status.value,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "system_context": self.system_context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }

class DebugSystem:
    """Debug system implementing Agans' 9 Rules."""

    def __init__(self, config: ServerConfig):
        """Initialize debug system."""
        self.config = config
        self.log_dir = config.debug_log_dir
        self.history_size = config.debug_history_size
        self.retention_days = config.debug_retention_days
        
        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize session storage
        self.sessions_dir = self.log_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Initialize index
        self.index_path = self.log_dir / "index.json"
        if not self.index_path.exists():
            self.index_path.write_text("{}")

    async def create_session(
        self,
        issue_type: IssueType,
        description: str,
        system_context: Dict
    ) -> DebugSession:
        """Create new debug session."""
        # Generate unique ID
        issue_id = f"{issue_type.value}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create session
        session = DebugSession(
            issue_id=issue_id,
            issue_type=issue_type,
            status=IssueStatus.NEW,
            description=description,
            steps=[],
            system_context=system_context,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save session
        await self._save_session(session)
        
        return session

    async def add_step(
        self,
        session: DebugSession,
        rule: str,
        action: str,
        result: str,
        observations: List[Observation]
    ) -> DebugSession:
        """Add debug step following Agans' rules."""
        step = DebugStep(
            rule=rule,
            action=action,
            result=result,
            observations=observations,
            timestamp=datetime.now()
        )
        
        session.steps.append(step)
        session.updated_at = datetime.now()
        
        await self._save_session(session)
        return session

    async def update_status(
        self,
        session: DebugSession,
        status: IssueStatus,
        resolution_notes: Optional[str] = None
    ) -> DebugSession:
        """Update debug session status."""
        session.status = status
        session.updated_at = datetime.now()
        
        if status == IssueStatus.RESOLVED:
            session.resolved_at = datetime.now()
            if resolution_notes:
                # Add resolution step
                await self.add_step(
                    session,
                    rule="Rule 9: If You Didn't Fix It, It Ain't Fixed",
                    action="Resolution verification",
                    result=resolution_notes,
                    observations=[]
                )
        
        await self._save_session(session)
        return session

    async def get_session(self, issue_id: str) -> Optional[DebugSession]:
        """Get debug session by ID."""
        session_path = self.sessions_dir / f"{issue_id}.json"
        if not session_path.exists():
            return None
        
        data = json.loads(session_path.read_text())
        return self._deserialize_session(data)

    async def list_sessions(
        self,
        status: Optional[IssueStatus] = None,
        issue_type: Optional[IssueType] = None
    ) -> List[DebugSession]:
        """List debug sessions with optional filters."""
        sessions = []
        for session_file in self.sessions_dir.glob("*.json"):
            data = json.loads(session_file.read_text())
            session = self._deserialize_session(data)
            
            if status and session.status != status:
                continue
            if issue_type and session.issue_type != issue_type:
                continue
            
            sessions.append(session)
        
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)

    async def cleanup_old_sessions(self) -> None:
        """Clean up old debug sessions."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        for session_file in self.sessions_dir.glob("*.json"):
            data = json.loads(session_file.read_text())
            updated_at = datetime.fromisoformat(data["updated_at"])
            
            if updated_at < cutoff:
                session_file.unlink()

    async def _save_session(self, session: DebugSession) -> None:
        """Save debug session to file."""
        session_path = self.sessions_dir / f"{session.issue_id}.json"
        session_path.write_text(json.dumps(session.to_dict(), indent=2))
        
        # Update index
        index = json.loads(self.index_path.read_text())
        index[session.issue_id] = {
            "type": session.issue_type.value,
            "status": session.status.value,
            "description": session.description,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
        self.index_path.write_text(json.dumps(index, indent=2))

    def _deserialize_session(self, data: Dict) -> DebugSession:
        """Create DebugSession from dictionary."""
        return DebugSession(
            issue_id=data["issue_id"],
            issue_type=IssueType(data["issue_type"]),
            status=IssueStatus(data["status"]),
            description=data["description"],
            steps=[
                DebugStep(
                    rule=step["rule"],
                    action=step["action"],
                    result=step["result"],
                    observations=[
                        Observation(
                            timestamp=datetime.fromisoformat(obs["timestamp"]),
                            description=obs["description"],
                            data=obs["data"],
                            context=obs["context"],
                            source=obs["source"]
                        )
                        for obs in step["observations"]
                    ],
                    timestamp=datetime.fromisoformat(step["timestamp"])
                )
                for step in data["steps"]
            ],
            system_context=data["system_context"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None
        )
