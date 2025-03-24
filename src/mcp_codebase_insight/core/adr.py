"""ADR (Architecture Decision Record) management module."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from slugify import slugify
import os

from pydantic import BaseModel

class ADRError(Exception):
    """Base class for ADR-related errors."""
    pass

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
        self.next_adr_number = 1  # Default to 1, will be updated in initialize()
        self.initialized = False
        self.adrs: Dict[UUID, ADR] = {}
        
    async def initialize(self):
        """Initialize the ADR manager.
        
        This method ensures the ADR directory exists and loads any existing ADRs.
        """
        if self.initialized:
            return
            
        try:
            # Ensure ADR directory exists
            self.adr_dir.mkdir(parents=True, exist_ok=True)
            
            # Calculate next ADR number from existing files
            max_number = 0
            for adr_file in self.adr_dir.glob("*.md"):
                try:
                    # Extract number from filename (e.g., "0001-title.md")
                    number = int(adr_file.name.split("-")[0])
                    max_number = max(max_number, number)
                except (ValueError, IndexError):
                    continue
            
            self.next_adr_number = max_number + 1
            
            # Load any existing ADRs
            for adr_file in self.adr_dir.glob("*.json"):
                if adr_file.is_file():
                    try:
                        with open(adr_file, "r") as f:
                            adr_data = json.load(f)
                            # Convert the loaded data into an ADR object
                            adr = ADR(**adr_data)
                            self.adrs[adr.id] = adr
                    except (json.JSONDecodeError, ValueError) as e:
                        # Log error but continue processing other files
                        print(f"Error loading ADR {adr_file}: {e}")
            
            self.initialized = True
        except Exception as e:
            print(f"Error initializing ADR manager: {e}")
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize ADR manager: {str(e)}")
            
    async def cleanup(self):
        """Clean up resources used by the ADR manager.
        
        This method ensures all ADRs are saved and resources are released.
        """
        if not self.initialized:
            return
            
        try:
            # Save any modified ADRs
            for adr in self.adrs.values():
                try:
                    await self._save_adr(adr)
                except Exception as e:
                    print(f"Error saving ADR {adr.id}: {e}")
            
            # Clear in-memory ADRs
            self.adrs.clear()
        except Exception as e:
            print(f"Error cleaning up ADR manager: {e}")
        finally:
            self.initialized = False
        
    async def create_adr(
        self,
        title: str,
        context: dict,
        options: List[dict],
        decision: str,
        consequences: Optional[Dict[str, List[str]]] = None
    ) -> ADR:
        """Create a new ADR."""
        adr_id = uuid4()
        now = datetime.utcnow()
        
        # Convert context dict to ADRContext
        adr_context = ADRContext(
            problem=context["problem"],
            constraints=context["constraints"],
            assumptions=context.get("assumptions"),
            background=context.get("background")
        )
        
        # Convert options list to ADROption objects
        adr_options = [
            ADROption(
                title=opt["title"],
                pros=opt["pros"],
                cons=opt["cons"],
                description=opt.get("description")
            )
            for opt in options
        ]
        
        adr = ADR(
            id=adr_id,
            title=title,
            status=ADRStatus.PROPOSED,
            context=adr_context,
            options=adr_options,
            decision=decision,
            consequences=consequences,
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
