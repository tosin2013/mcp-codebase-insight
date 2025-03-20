"""ADR (Architecture Decision Record) management module."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

class ADRStatus(str, Enum):
    """ADR status enumeration."""
    
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"

class ADROption(BaseModel):
    """ADR option model."""
    
    title: str
    pros: List[str]
    cons: List[str]
    description: Optional[str] = None

class ADRContext(BaseModel):
    """ADR context model."""
    
    problem: str
    constraints: List[str]
    assumptions: Optional[List[str]] = None
    background: Optional[str] = None

class ADR(BaseModel):
    """ADR model."""
    
    id: UUID
    title: str
    status: ADRStatus
    context: ADRContext
    options: List[ADROption]
    decision: str
    consequences: Optional[Dict[str, List[str]]] = None
    metadata: Optional[Dict[str, str]] = None
    created_at: datetime
    updated_at: datetime
    superseded_by: Optional[UUID] = None

class ADRManager:
    """ADR manager for handling architecture decision records."""
    
    def __init__(self, config):
        """Initialize ADR manager."""
        self.config = config
        self.adr_dir = config.adr_dir
        self.adr_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_adr(
        self,
        title: str,
        context: Dict,
        options: List[Dict],
        decision: str,
        consequences: Optional[Dict[str, List[str]]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> ADR:
        """Create a new ADR."""
        now = datetime.utcnow()
        adr = ADR(
            id=uuid4(),
            title=title,
            status=ADRStatus.PROPOSED,
            context=ADRContext(**context),
            options=[ADROption(**opt) for opt in options],
            decision=decision,
            consequences=consequences,
            metadata=metadata,
            created_at=now,
            updated_at=now
        )
        
        await self._save_adr(adr)
        return adr
    
    async def get_adr(self, adr_id: UUID) -> Optional[ADR]:
        """Get ADR by ID."""
        adr_path = self.adr_dir / f"{adr_id}.json"
        if not adr_path.exists():
            return None
            
        with open(adr_path) as f:
            data = json.load(f)
            return ADR(**data)
    
    async def update_adr(
        self,
        adr_id: UUID,
        status: Optional[ADRStatus] = None,
        superseded_by: Optional[UUID] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[ADR]:
        """Update ADR status and metadata."""
        adr = await self.get_adr(adr_id)
        if not adr:
            return None
            
        if status:
            adr.status = status
        if superseded_by:
            adr.superseded_by = superseded_by
        if metadata:
            adr.metadata = {**(adr.metadata or {}), **metadata}
            
        adr.updated_at = datetime.utcnow()
        await self._save_adr(adr)
        return adr
    
    async def list_adrs(
        self,
        status: Optional[ADRStatus] = None
    ) -> List[ADR]:
        """List all ADRs, optionally filtered by status."""
        adrs = []
        for path in self.adr_dir.glob("*.json"):
            with open(path) as f:
                data = json.load(f)
                adr = ADR(**data)
                if not status or adr.status == status:
                    adrs.append(adr)
        return sorted(adrs, key=lambda x: x.created_at)
    
    async def _save_adr(self, adr: ADR) -> None:
        """Save ADR to file."""
        adr_path = self.adr_dir / f"{adr.id}.json"
        with open(adr_path, "w") as f:
            json.dump(adr.model_dump(), f, indent=2, default=str)
