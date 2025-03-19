from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
from git import Repo

from .config import ServerConfig
from .vector_store import VectorStore
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PatternType(Enum):
    """Type of knowledge pattern."""
    CODE = "code"
    ARCHITECTURE = "architecture"
    DEBUG = "debug"
    SOLUTION = "solution"
    BEST_PRACTICE = "best_practice"

class ConfidenceLevel(Enum):
    """Confidence level in a pattern."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EXPERIMENTAL = "experimental"

@dataclass
class Pattern:
    """Knowledge pattern."""
    id: str
    type: PatternType
    name: str
    description: str
    content: str
    examples: List[str]
    context: Dict
    tags: Set[str]
    confidence: ConfidenceLevel
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    success_rate: float = 0.0
    related_patterns: List[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "examples": self.examples,
            "context": self.context,
            "tags": list(self.tags),
            "confidence": self.confidence.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "related_patterns": self.related_patterns or []
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Pattern":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=PatternType(data["type"]),
            name=data["name"],
            description=data["description"],
            content=data["content"],
            examples=data["examples"],
            context=data["context"],
            tags=set(data["tags"]),
            confidence=ConfidenceLevel(data["confidence"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            usage_count=data["usage_count"],
            success_rate=data["success_rate"],
            related_patterns=data.get("related_patterns", [])
        )

class KnowledgeBase:
    """Manages knowledge patterns and learning."""

    def __init__(self, config: ServerConfig, vector_store: VectorStore):
        """Initialize knowledge base."""
        self.config = config
        self.vector_store = vector_store
        self.storage_dir = config.kb_storage_dir
        self.max_patterns = config.kb_max_patterns
        
        # Ensure directories exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize pattern storage
        self.patterns_dir = self.storage_dir / "patterns"
        self.patterns_dir.mkdir(exist_ok=True)
        
        # Initialize index
        self.index_path = self.storage_dir / "index.json"
        if not self.index_path.exists():
            self.index_path.write_text("{}")

    async def store_pattern(
        self,
        type: PatternType,
        name: str,
        description: str,
        content: str,
        examples: List[str],
        context: Dict,
        tags: Set[str],
        confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    ) -> Pattern:
        """Store new knowledge pattern."""
        # Generate unique ID
        pattern_id = f"{type.value}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create pattern
        pattern = Pattern(
            id=pattern_id,
            type=type,
            name=name,
            description=description,
            content=content,
            examples=examples,
            context=context,
            tags=tags,
            confidence=confidence,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store in vector database
        text = f"{name} {description} {content}"
        await self.vector_store.store(
            text=text,
            metadata=pattern.to_dict()
        )
        
        # Save pattern
        await self._save_pattern(pattern)
        
        return pattern

    async def find_similar_patterns(
        self,
        text: str,
        type: Optional[PatternType] = None,
        min_confidence: Optional[ConfidenceLevel] = None,
        limit: int = 5
    ) -> List[Pattern]:
        """Find similar patterns using vector similarity."""
        # Prepare filter
        filter_params = {"must": []}
        if type:
            filter_params["must"].append({
                "key": "type",
                "match": {"value": type.value}
            })
        if min_confidence:
            confidence_levels = [
                level.value
                for level in ConfidenceLevel
                if level.value >= min_confidence.value
            ]
            filter_params["must"].append({
                "key": "confidence",
                "match": {"any": confidence_levels}
            })
        
        # Search vector database
        results = await self.vector_store.search(
            text=text,
            filter_params=filter_params,
            limit=limit
        )
        
        # Convert to patterns
        patterns = []
        for result in results:
            pattern = Pattern.from_dict(result.payload)
            pattern.similarity_score = result.score
            patterns.append(pattern)
        
        return patterns

    async def update_pattern(
        self,
        pattern: Pattern,
        updates: Dict,
        success: Optional[bool] = None
    ) -> Pattern:
        """Update existing pattern."""
        # Update fields
        for key, value in updates.items():
            if hasattr(pattern, key):
                setattr(pattern, key, value)
        
        # Update usage statistics if success provided
        if success is not None:
            pattern.usage_count += 1
            total_successes = pattern.success_rate * (pattern.usage_count - 1)
            total_successes += 1 if success else 0
            pattern.success_rate = total_successes / pattern.usage_count
        
        pattern.updated_at = datetime.now()
        
        # Update vector database
        text = f"{pattern.name} {pattern.description} {pattern.content}"
        await self.vector_store.update(
            id=pattern.id,
            text=text,
            metadata=pattern.to_dict()
        )
        
        # Save updated pattern
        await self._save_pattern(pattern)
        
        return pattern

    async def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get pattern by ID."""
        pattern_path = self.patterns_dir / f"{pattern_id}.json"
        if not pattern_path.exists():
            return None
        
        data = json.loads(pattern_path.read_text())
        return Pattern.from_dict(data)

    async def list_patterns(
        self,
        type: Optional[PatternType] = None,
        tags: Optional[Set[str]] = None,
        min_confidence: Optional[ConfidenceLevel] = None
    ) -> List[Pattern]:
        """List patterns with optional filters."""
        patterns = []
        for pattern_file in self.patterns_dir.glob("*.json"):
            data = json.loads(pattern_file.read_text())
            pattern = Pattern.from_dict(data)
            
            if type and pattern.type != type:
                continue
            if tags and not tags.issubset(pattern.tags):
                continue
            if min_confidence and pattern.confidence.value < min_confidence.value:
                continue
            
            patterns.append(pattern)
        
        return sorted(patterns, key=lambda p: p.updated_at, reverse=True)

    async def find_related_patterns(
        self,
        pattern: Pattern,
        limit: int = 5
    ) -> List[Pattern]:
        """Find patterns related to given pattern."""
        # Use pattern content for similarity search
        text = f"{pattern.name} {pattern.description} {pattern.content}"
        results = await self.vector_store.search(
            text=text,
            filter_params={
                "must_not": [
                    {"key": "id", "match": {"value": pattern.id}}
                ]
            },
            limit=limit + 1  # Add 1 to account for the pattern itself
        )
        
        # Convert to patterns
        related = []
        for result in results:
            if result.payload["id"] != pattern.id:
                related_pattern = Pattern.from_dict(result.payload)
                related_pattern.similarity_score = result.score
                related.append(related_pattern)
        
        return related[:limit]

    async def _save_pattern(self, pattern: Pattern) -> None:
        """Save pattern to file."""
        pattern_path = self.patterns_dir / f"{pattern.id}.json"
        pattern_path.write_text(json.dumps(pattern.to_dict(), indent=2))
        
        # Update index
        index = json.loads(self.index_path.read_text())
        index[pattern.id] = {
            "type": pattern.type.value,
            "name": pattern.name,
            "confidence": pattern.confidence.value,
            "updated_at": pattern.updated_at.isoformat()
        }
        self.index_path.write_text(json.dumps(index, indent=2))
        
        # Check pattern limit
        if len(index) > self.max_patterns:
            await self._cleanup_old_patterns()

    async def _cleanup_old_patterns(self) -> None:
        """Remove old patterns when limit is reached."""
        patterns = await self.list_patterns()
        patterns.sort(key=lambda p: (p.usage_count, p.updated_at))
        
        # Remove oldest, least used patterns
        while len(patterns) > self.max_patterns:
            pattern = patterns.pop(0)
            pattern_path = self.patterns_dir / f"{pattern.id}.json"
            pattern_path.unlink()
            
            # Update index
            index = json.loads(self.index_path.read_text())
            del index[pattern.id]
            self.index_path.write_text(json.dumps(index, indent=2))
            
            # Remove from vector store
            await self.vector_store.delete(pattern.id)
