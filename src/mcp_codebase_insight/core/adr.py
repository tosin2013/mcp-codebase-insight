"""Architectural Decision Records (ADR) management."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter
import re

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.errors import ADRError
from mcp_codebase_insight.utils.logger import get_logger

logger = get_logger(__name__)

class ADRStatus(str, Enum):
    """Status of an architectural decision."""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    AMENDED = "amended"

@dataclass
class ADROption:
    """An option considered in an architectural decision."""
    title: str
    description: str
    pros: List[str]
    cons: List[str]
    implications: List[str]

@dataclass
class ADR:
    """An architectural decision record."""
    id: str
    title: str
    status: ADRStatus
    context: Dict[str, Any]
    options: List[ADROption]
    decision: str
    consequences: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    superseded_by: Optional[str] = None
    amends: Optional[str] = None

class ADRManager:
    """Manager for architectural decision records."""

    def __init__(self, config: ServerConfig):
        """Initialize ADR manager."""
        self.config = config
        self.adr_dir = config.adr_dir
        self.template_path = config.adr_template_path
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        self._load_template()
        self._load_adrs()

    def _load_template(self):
        """Load ADR template."""
        try:
            if not self.template_path.exists():
                self._create_default_template()
            with open(self.template_path, "r") as f:
                self.template = f.read()
        except Exception as e:
            raise ADRError(f"Failed to load template: {e}")

    def _create_default_template(self):
        """Create default ADR template."""
        try:
            template = """# {title}

## Status

{status}

## Context

{context}

## Options Considered

{options}

## Decision

{decision}

## Consequences

{consequences}

## Metadata

{metadata}
"""
            self.template_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.template_path, "w") as f:
                f.write(template)
        except Exception as e:
            raise ADRError(f"Failed to create template: {e}")

    def _load_adrs(self):
        """Load existing ADRs."""
        try:
            self.adrs = {}
            for path in self.adr_dir.glob("*.md"):
                adr = self._parse_adr_file(path)
                self.adrs[adr.id] = adr
        except Exception as e:
            raise ADRError(f"Failed to load ADRs: {e}")

    def _parse_adr_file(self, path: Path) -> ADR:
        """Parse an ADR file."""
        try:
            post = frontmatter.load(path)
            metadata = post.metadata
            content = post.content
            
            # Extract ID from filename
            match = re.match(r"(\d+)_.+\.md", path.name)
            if not match:
                raise ADRError(f"Invalid ADR filename: {path.name}")
            adr_id = match.group(1)
            
            # Parse sections
            sections = self._parse_sections(content)
            
            # Parse options
            options = []
            if "Options Considered" in sections:
                options_text = sections["Options Considered"].split("\n\n")
                for opt_text in options_text:
                    if not opt_text.strip():
                        continue
                    opt_sections = self._parse_sections(opt_text)
                    options.append(ADROption(
                        title=opt_sections.get("title", ""),
                        description=opt_sections.get("description", ""),
                        pros=opt_sections.get("pros", "").split("\n"),
                        cons=opt_sections.get("cons", "").split("\n"),
                        implications=opt_sections.get("implications", "").split("\n")
                    ))
            
            return ADR(
                id=adr_id,
                title=sections.get("title", ""),
                status=ADRStatus(sections.get("Status", "proposed").lower()),
                context=self._parse_context(sections.get("Context", "")),
                options=options,
                decision=sections.get("Decision", ""),
                consequences=sections.get("Consequences", "").split("\n"),
                metadata=metadata,
                created_at=datetime.fromisoformat(metadata.get("created_at", datetime.utcnow().isoformat())),
                updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.utcnow().isoformat())),
                superseded_by=metadata.get("superseded_by"),
                amends=metadata.get("amends")
            )
        except Exception as e:
            raise ADRError(f"Failed to parse ADR file: {e}")

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown sections."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split("\n"):
            if line.startswith("# "):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line[2:].strip()
                current_content = []
            elif line.startswith("## "):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()
        
        return sections

    def _parse_context(self, context: str) -> Dict[str, Any]:
        """Parse context section into structured data."""
        try:
            # Simple key-value parsing for now
            result = {}
            current_key = None
            current_value = []
            
            for line in context.split("\n"):
                if line.startswith("### "):
                    if current_key:
                        result[current_key] = "\n".join(current_value).strip()
                    current_key = line[4:].strip()
                    current_value = []
                else:
                    current_value.append(line)
            
            if current_key:
                result[current_key] = "\n".join(current_value).strip()
            
            return result
        except Exception:
            # Fall back to raw text if parsing fails
            return {"text": context}

    def _format_adr(self, adr: ADR) -> str:
        """Format ADR as markdown."""
        try:
            # Format options
            options_text = []
            for opt in adr.options:
                options_text.append(f"""### {opt.title}

{opt.description}

#### Pros

{chr(10).join(f'- {p}' for p in opt.pros)}

#### Cons

{chr(10).join(f'- {c}' for c in opt.cons)}

#### Implications

{chr(10).join(f'- {i}' for i in opt.implications)}
""")
            
            # Format context
            context_text = []
            for key, value in adr.context.items():
                context_text.append(f"""### {key}

{value}
""")
            
            # Format consequences
            consequences_text = "\n".join(f"- {c}" for c in adr.consequences)
            
            # Format metadata
            metadata_text = []
            for key, value in adr.metadata.items():
                metadata_text.append(f"- {key}: {value}")
            
            # Apply template
            content = self.template.format(
                title=adr.title,
                status=adr.status.value,
                context="\n\n".join(context_text),
                options="\n\n".join(options_text),
                decision=adr.decision,
                consequences=consequences_text,
                metadata="\n".join(metadata_text)
            )
            
            # Add frontmatter
            metadata = {
                "created_at": adr.created_at.isoformat(),
                "updated_at": adr.updated_at.isoformat(),
                **adr.metadata
            }
            if adr.superseded_by:
                metadata["superseded_by"] = adr.superseded_by
            if adr.amends:
                metadata["amends"] = adr.amends
            
            return frontmatter.dumps(frontmatter.Post(content, **metadata))
        except Exception as e:
            raise ADRError(f"Failed to format ADR: {e}")

    def _get_next_id(self) -> str:
        """Get next ADR ID."""
        try:
            existing_ids = [int(adr.id) for adr in self.adrs.values()]
            return str(max(existing_ids, default=0) + 1).zfill(3)
        except Exception as e:
            raise ADRError(f"Failed to generate ADR ID: {e}")

    async def create_adr(
        self,
        title: str,
        context: Dict[str, Any],
        options: List[ADROption],
        decision: str,
        consequences: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ADR:
        """Create a new ADR."""
        try:
            adr_id = self._get_next_id()
            now = datetime.utcnow()
            
            adr = ADR(
                id=adr_id,
                title=title,
                status=ADRStatus.PROPOSED,
                context=context,
                options=options,
                decision=decision,
                consequences=consequences or [],
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            
            # Save ADR
            content = self._format_adr(adr)
            path = self.adr_dir / f"{adr_id}_{self._slugify(title)}.md"
            with open(path, "w") as f:
                f.write(content)
            
            self.adrs[adr_id] = adr
            logger.info(f"Created ADR {adr_id}: {title}")
            
            return adr
        except Exception as e:
            raise ADRError(f"Failed to create ADR: {e}")

    def _slugify(self, text: str) -> str:
        """Convert text to slug."""
        return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')

    async def get_adr(self, adr_id: str) -> Optional[ADR]:
        """Get ADR by ID."""
        return self.adrs.get(adr_id)

    async def update_adr(
        self,
        adr_id: str,
        status: Optional[ADRStatus] = None,
        decision: Optional[str] = None,
        consequences: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ADR:
        """Update an ADR."""
        try:
            adr = self.adrs.get(adr_id)
            if not adr:
                raise ADRError(f"ADR not found: {adr_id}")
            
            if status is not None:
                adr.status = status
            if decision is not None:
                adr.decision = decision
            if consequences is not None:
                adr.consequences = consequences
            if metadata is not None:
                adr.metadata.update(metadata)
            
            adr.updated_at = datetime.utcnow()
            
            # Save ADR
            content = self._format_adr(adr)
            path = self.adr_dir / f"{adr_id}_{self._slugify(adr.title)}.md"
            with open(path, "w") as f:
                f.write(content)
            
            logger.info(f"Updated ADR {adr_id}")
            return adr
        except Exception as e:
            raise ADRError(f"Failed to update ADR: {e}")

    async def list_adrs(
        self,
        status: Optional[ADRStatus] = None
    ) -> List[ADR]:
        """List ADRs with optional status filter."""
        adrs = list(self.adrs.values())
        
        if status:
            adrs = [a for a in adrs if a.status == status]
        
        return sorted(adrs, key=lambda a: int(a.id))

    async def supersede_adr(
        self,
        old_id: str,
        new_id: str
    ) -> ADR:
        """Mark an ADR as superseded by another."""
        try:
            old_adr = self.adrs.get(old_id)
            new_adr = self.adrs.get(new_id)
            if not old_adr or not new_adr:
                raise ADRError("ADR not found")
            
            old_adr.status = ADRStatus.SUPERSEDED
            old_adr.superseded_by = new_id
            old_adr.updated_at = datetime.utcnow()
            
            # Save old ADR
            content = self._format_adr(old_adr)
            path = self.adr_dir / f"{old_id}_{self._slugify(old_adr.title)}.md"
            with open(path, "w") as f:
                f.write(content)
            
            logger.info(f"ADR {old_id} superseded by {new_id}")
            return old_adr
        except Exception as e:
            raise ADRError(f"Failed to supersede ADR: {e}")
