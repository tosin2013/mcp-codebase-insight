from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import frontmatter
import yaml
from git import Repo

from .config import ServerConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ADRStatus(Enum):
    """Status of an architectural decision."""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    AMENDED = "amended"

class ImpactLevel(Enum):
    """Impact level of an architectural decision."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Complexity(Enum):
    """Complexity level of implementation."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ImplementationStatus(Enum):
    """Status of ADR implementation."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

@dataclass
class ADRMetadata:
    """Metadata for an architectural decision record."""
    version: str = "1.0"
    last_modified: datetime = None
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    complexity: Complexity = Complexity.MEDIUM
    implementation_status: ImplementationStatus = ImplementationStatus.NOT_STARTED
    confidence_level: int = 80  # 0-100

    def to_dict(self) -> Dict:
        """Convert metadata to dictionary."""
        return {
            "version": self.version,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "impact_level": self.impact_level.value,
            "complexity": self.complexity.value,
            "implementation_status": self.implementation_status.value,
            "confidence_level": self.confidence_level
        }

class ADRManager:
    """Manages architectural decision records."""

    def __init__(self, config: ServerConfig):
        """Initialize ADR manager."""
        self.config = config
        self.adr_dir = config.adr_dir
        self.template_path = config.adr_template_path
        self.index_path = config.adr_index_path
        
        # Ensure directories exist
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        self.template_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    async def create_adr(
        self,
        title: str,
        technical_context: str,
        business_context: str,
        current_architecture: str,
        technical_drivers: List[str],
        business_drivers: List[str],
        options: List[Dict],
        chosen_option: str,
        justification: str,
        consequences: Dict[str, List[str]],
        implementation: Dict[str, str],
        metadata: Optional[ADRMetadata] = None
    ) -> Path:
        """Create a new ADR."""
        # Generate ADR number
        adr_number = self._get_next_adr_number()
        
        # Load template
        template = await self._load_template()
        
        # Prepare ADR content
        adr_content = template.format(
            title=title,
            status=ADRStatus.PROPOSED.value,
            date=datetime.now().strftime("%Y-%m-%d"),
            deciders="",  # To be filled by reviewers
            technical_story="",  # Optional reference to technical story
            technical_context=technical_context,
            business_context=business_context,
            current_architecture=current_architecture,
            technical_drivers="\n* ".join(technical_drivers),
            business_drivers="\n* ".join(business_drivers),
            option_1_name=options[0]["name"],
            option_1_description=options[0]["description"],
            option_1_technical_fit=options[0]["technical_fit"],
            option_1_business_impact=options[0]["business_impact"],
            option_1_risks=options[0]["risks"],
            option_1_cost=options[0]["cost"],
            option_2_name=options[1]["name"] if len(options) > 1 else "",
            option_2_description=options[1]["description"] if len(options) > 1 else "",
            option_2_technical_fit=options[1]["technical_fit"] if len(options) > 1 else "",
            option_2_business_impact=options[1]["business_impact"] if len(options) > 1 else "",
            option_2_risks=options[1]["risks"] if len(options) > 1 else "",
            option_2_cost=options[1]["cost"] if len(options) > 1 else "",
            chosen_option=chosen_option,
            decision_justification=justification,
            positive_consequences="\n* ".join(consequences.get("positive", [])),
            negative_consequences="\n* ".join(consequences.get("negative", [])),
            neutral_consequences="\n* ".join(consequences.get("neutral", [])),
            technical_implementation=implementation.get("technical", ""),
            migration_strategy=implementation.get("migration", ""),
            validation_criteria=implementation.get("validation", ""),
            related_decisions="",  # To be filled later
            notes="",  # Optional notes
            references="",  # Optional references
            update_1_date="",  # For future updates
            update_1_change="",
            update_1_reason="",
            update_1_impact="",
            last_modified=datetime.now().isoformat(),
            impact_level=metadata.impact_level.value if metadata else ImpactLevel.MEDIUM.value,
            complexity=metadata.complexity.value if metadata else Complexity.MEDIUM.value,
            implementation_status=metadata.implementation_status.value if metadata else ImplementationStatus.NOT_STARTED.value,
            confidence_level=metadata.confidence_level if metadata else 80
        )
        
        # Save ADR
        adr_path = self.adr_dir / f"{adr_number:04d}-{self._slugify(title)}.md"
        adr_path.write_text(adr_content)
        
        # Update index
        await self._update_index(adr_number, title, ADRStatus.PROPOSED)
        
        return adr_path

    async def update_adr(
        self,
        adr_path: Path,
        changes: Dict[str, any],
        reason: str
    ) -> None:
        """Update an existing ADR."""
        if not adr_path.exists():
            raise FileNotFoundError(f"ADR not found: {adr_path}")
        
        # Load current ADR
        adr = frontmatter.load(adr_path)
        
        # Create update entry
        update = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "changes": changes,
            "reason": reason
        }
        
        # Add update to ADR
        if "updates" not in adr:
            adr["updates"] = []
        adr["updates"].append(update)
        
        # Update metadata
        adr["last_modified"] = datetime.now().isoformat()
        
        # Save updated ADR
        frontmatter.dump(adr, adr_path)
        
        # Update index if status changed
        if "status" in changes:
            adr_number = int(adr_path.stem.split("-")[0])
            await self._update_index(adr_number, adr["title"], ADRStatus(changes["status"]))

    async def get_adr(self, adr_path: Path) -> Dict:
        """Get ADR content and metadata."""
        if not adr_path.exists():
            raise FileNotFoundError(f"ADR not found: {adr_path}")
        
        adr = frontmatter.load(adr_path)
        return {
            "content": adr.content,
            "metadata": adr.metadata
        }

    async def list_adrs(self) -> List[Dict]:
        """List all ADRs with their metadata."""
        adrs = []
        for adr_file in sorted(self.adr_dir.glob("*.md")):
            if adr_file.name != "index.md":
                adr = frontmatter.load(adr_file)
                adrs.append({
                    "number": int(adr_file.stem.split("-")[0]),
                    "title": adr["title"],
                    "status": adr["status"],
                    "date": adr["date"],
                    "path": adr_file
                })
        return adrs

    async def _load_template(self) -> str:
        """Load ADR template."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"ADR template not found: {self.template_path}")
        return self.template_path.read_text()

    def _get_next_adr_number(self) -> int:
        """Get next ADR number."""
        existing_adrs = list(self.adr_dir.glob("[0-9]*.md"))
        if not existing_adrs:
            return 1
        return max(int(adr.stem.split("-")[0]) for adr in existing_adrs) + 1

    async def _update_index(self, number: int, title: str, status: ADRStatus) -> None:
        """Update ADR index."""
        if self.index_path.exists():
            content = self.index_path.read_text()
            lines = content.splitlines()
        else:
            lines = ["# Architectural Decision Records", "", "## Index", ""]
        
        # Find or create entry
        entry = f"* [{number:04d}] {title} - {status.value}"
        entry_prefix = f"* [{number:04d}]"
        
        for i, line in enumerate(lines):
            if line.startswith(entry_prefix):
                lines[i] = entry
                break
        else:
            lines.append(entry)
        
        # Save updated index
        self.index_path.write_text("\n".join(lines))

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        return text.lower().replace(" ", "-").replace("_", "-")
