from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
import structlog

from .config import ServerConfig
from .knowledge import KnowledgeBase, Pattern, PatternType
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PromptType(Enum):
    """Type of prompt template."""
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE = "architecture"
    DEBUG = "debug"
    ADR = "adr"
    TEST = "test"
    DOCUMENTATION = "documentation"
    META = "meta"

class PromptContext(Enum):
    """Context type for prompt."""
    CODE = "code"
    SYSTEM = "system"
    USER = "user"
    HISTORY = "history"
    PATTERNS = "patterns"
    DOCUMENTATION = "documentation"

@dataclass
class PromptTemplate:
    """Template for generating prompts."""
    id: str
    type: PromptType
    name: str
    description: str
    template: str
    required_context: Set[PromptContext]
    examples: List[Dict]
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    success_rate: float = 0.0
    version: int = 1

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "required_context": [ctx.value for ctx in self.required_context],
            "examples": self.examples,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PromptTemplate":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=PromptType(data["type"]),
            name=data["name"],
            description=data["description"],
            template=data["template"],
            required_context={PromptContext(ctx) for ctx in data["required_context"]},
            examples=data["examples"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            usage_count=data["usage_count"],
            success_rate=data["success_rate"],
            version=data["version"]
        )

class PromptManager:
    """Manages prompt templates and evolution."""

    def __init__(self, config: ServerConfig, knowledge_base: KnowledgeBase):
        """Initialize prompt manager."""
        self.config = config
        self.knowledge_base = knowledge_base
        self.storage_dir = config.kb_storage_dir / "prompts"
        
        # Ensure directories exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize index
        self.index_path = self.storage_dir / "index.json"
        if not self.index_path.exists():
            self.index_path.write_text("{}")

    async def create_template(
        self,
        type: PromptType,
        name: str,
        description: str,
        template: str,
        required_context: Set[PromptContext],
        examples: List[Dict]
    ) -> PromptTemplate:
        """Create new prompt template."""
        # Generate unique ID
        template_id = f"{type.value}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create template
        prompt = PromptTemplate(
            id=template_id,
            type=type,
            name=name,
            description=description,
            template=template,
            required_context=required_context,
            examples=examples,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save template
        await self._save_template(prompt)
        
        # Store as pattern in knowledge base
        await self.knowledge_base.store_pattern(
            type=PatternType.BEST_PRACTICE,
            name=f"Prompt Template: {name}",
            description=description,
            content=template,
            examples=[json.dumps(ex, indent=2) for ex in examples],
            context={"type": type.value, "required_context": [ctx.value for ctx in required_context]},
            tags={"prompt", "template", type.value}
        )
        
        return prompt

    async def evolve_template(
        self,
        template: PromptTemplate,
        new_template: str,
        reason: str,
        success_rate: Optional[float] = None
    ) -> PromptTemplate:
        """Evolve prompt template based on feedback."""
        # Create new version
        evolved = PromptTemplate(
            id=f"{template.id}-v{template.version + 1}",
            type=template.type,
            name=template.name,
            description=template.description,
            template=new_template,
            required_context=template.required_context,
            examples=template.examples,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            usage_count=0,
            success_rate=success_rate or template.success_rate,
            version=template.version + 1
        )
        
        # Save new version
        await self._save_template(evolved)
        
        # Store evolution in knowledge base
        await self.knowledge_base.store_pattern(
            type=PatternType.BEST_PRACTICE,
            name=f"Prompt Evolution: {template.name} v{evolved.version}",
            description=f"Evolution of prompt template {template.name}\nReason: {reason}",
            content=f"Previous:\n{template.template}\n\nNew:\n{new_template}",
            examples=[],
            context={
                "original_id": template.id,
                "success_rate": success_rate,
                "version": evolved.version
            },
            tags={"prompt", "evolution", template.type.value}
        )
        
        return evolved

    async def get_template(
        self,
        template_id: str,
        version: Optional[int] = None
    ) -> Optional[PromptTemplate]:
        """Get prompt template by ID and optional version."""
        if version:
            template_path = self.storage_dir / f"{template_id}-v{version}.json"
        else:
            # Get latest version
            versions = list(self.storage_dir.glob(f"{template_id}*.json"))
            if not versions:
                return None
            template_path = max(versions, key=lambda p: int(p.stem.split("-v")[-1]))
        
        if not template_path.exists():
            return None
        
        data = json.loads(template_path.read_text())
        return PromptTemplate.from_dict(data)

    async def list_templates(
        self,
        type: Optional[PromptType] = None,
        required_context: Optional[Set[PromptContext]] = None
    ) -> List[PromptTemplate]:
        """List prompt templates with optional filters."""
        templates = []
        for template_file in self.storage_dir.glob("*.json"):
            data = json.loads(template_file.read_text())
            template = PromptTemplate.from_dict(data)
            
            if type and template.type != type:
                continue
            if required_context and not required_context.issubset(template.required_context):
                continue
            
            templates.append(template)
        
        return sorted(templates, key=lambda t: t.updated_at, reverse=True)

    async def generate_prompt(
        self,
        type: PromptType,
        context: Dict[PromptContext, str]
    ) -> str:
        """Generate prompt from template and context."""
        # Find latest template of given type
        templates = await self.list_templates(type=type)
        if not templates:
            raise ValueError(f"No template found for type: {type}")
        
        template = templates[0]  # Latest version
        
        # Validate required context
        missing = template.required_context - set(context.keys())
        if missing:
            raise ValueError(f"Missing required context: {missing}")
        
        # Generate prompt
        prompt = template.template
        for ctx_type, ctx_value in context.items():
            placeholder = f"{{{ctx_type.value}}}"
            prompt = prompt.replace(placeholder, ctx_value)
        
        return prompt

    async def record_feedback(
        self,
        template: PromptTemplate,
        success: bool,
        feedback: Optional[str] = None
    ) -> None:
        """Record feedback on prompt template usage."""
        # Update usage statistics
        template.usage_count += 1
        total_successes = template.success_rate * (template.usage_count - 1)
        total_successes += 1 if success else 0
        template.success_rate = total_successes / template.usage_count
        
        template.updated_at = datetime.now()
        
        # Save updated template
        await self._save_template(template)
        
        # Store feedback in knowledge base if provided
        if feedback:
            await self.knowledge_base.store_pattern(
                type=PatternType.BEST_PRACTICE,
                name=f"Prompt Feedback: {template.name}",
                description=feedback,
                content=template.template,
                examples=[],
                context={
                    "template_id": template.id,
                    "version": template.version,
                    "success": success,
                    "success_rate": template.success_rate
                },
                tags={"prompt", "feedback", template.type.value}
            )

    async def _save_template(self, template: PromptTemplate) -> None:
        """Save prompt template to file."""
        template_path = self.storage_dir / f"{template.id}.json"
        template_path.write_text(json.dumps(template.to_dict(), indent=2))
        
        # Update index
        index = json.loads(self.index_path.read_text())
        index[template.id] = {
            "type": template.type.value,
            "name": template.name,
            "version": template.version,
            "success_rate": template.success_rate,
            "updated_at": template.updated_at.isoformat()
        }
        self.index_path.write_text(json.dumps(index, indent=2))
