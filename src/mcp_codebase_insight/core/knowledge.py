"""Knowledge base management."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.vector_store import VectorStore
from mcp_codebase_insight.core.errors import KnowledgeBaseError
from mcp_codebase_insight.utils.logger import get_logger

logger = get_logger(__name__)

class PatternType(str, Enum):
    """Types of knowledge patterns."""
    CODE = "code"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DEPLOYMENT = "deployment"

class ConfidenceLevel(str, Enum):
    """Confidence levels for patterns."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Pattern:
    """Knowledge pattern."""
    id: str
    name: str
    description: str
    type: PatternType
    confidence: ConfidenceLevel
    examples: List[str]
    metadata: Dict[str, Any]
    similarity_score: Optional[float] = None

class KnowledgeBase:
    """Knowledge base for storing and retrieving patterns."""

    def __init__(self, config: ServerConfig, vector_store: VectorStore):
        """Initialize knowledge base."""
        self.config = config
        self.vector_store = vector_store
        self.storage_dir = config.kb_storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_file = self.storage_dir / "patterns.json"
        self._load_patterns()

    def _load_patterns(self):
        """Load patterns from storage."""
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, "r") as f:
                    patterns = json.load(f)
                self.patterns = {
                    p["id"]: Pattern(**p)
                    for p in patterns
                }
            else:
                self.patterns = {}
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to load patterns: {e}")

    def _save_patterns(self):
        """Save patterns to storage."""
        try:
            patterns = [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "type": p.type.value,
                    "confidence": p.confidence.value,
                    "examples": p.examples,
                    "metadata": p.metadata
                }
                for p in self.patterns.values()
            ]
            with open(self.patterns_file, "w") as f:
                json.dump(patterns, f, indent=2)
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to save patterns: {e}")

    async def add_pattern(
        self,
        name: str,
        description: str,
        type: PatternType,
        confidence: ConfidenceLevel,
        examples: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Pattern:
        """Add a new pattern."""
        try:
            from uuid import uuid4
            pattern_id = str(uuid4())
            
            pattern = Pattern(
                id=pattern_id,
                name=name,
                description=description,
                type=type,
                confidence=confidence,
                examples=examples,
                metadata=metadata or {}
            )
            
            # Add to vector store
            texts = [description] + examples
            meta = {
                "id": pattern_id,
                "name": name,
                "type": type.value,
                "confidence": confidence.value
            }
            metas = [meta] * len(texts)
            
            self.vector_store.add_points(
                texts=texts,
                metadata=metas,
                ids=[f"{pattern_id}_{i}" for i in range(len(texts))]
            )
            
            # Add to local storage
            self.patterns[pattern_id] = pattern
            self._save_patterns()
            
            return pattern
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to add pattern: {e}")

    async def find_similar_patterns(
        self,
        text: str,
        type: Optional[PatternType] = None,
        limit: int = 5
    ) -> List[Pattern]:
        """Find similar patterns."""
        try:
            filter = {"type": type.value} if type else None
            results = self.vector_store.search(
                query=text,
                limit=limit,
                filter=filter
            )
            
            patterns = []
            seen_ids = set()
            
            for r in results:
                pattern_id = r["payload"]["id"]
                if pattern_id not in seen_ids:
                    pattern = self.patterns[pattern_id]
                    pattern.similarity_score = r["score"]
                    patterns.append(pattern)
                    seen_ids.add(pattern_id)
            
            return patterns
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to find patterns: {e}")

    async def delete_pattern(self, pattern_id: str):
        """Delete a pattern."""
        try:
            if pattern_id not in self.patterns:
                raise KnowledgeBaseError(f"Pattern not found: {pattern_id}")
            
            # Delete from vector store
            pattern = self.patterns[pattern_id]
            ids = [
                f"{pattern_id}_{i}"
                for i in range(len(pattern.examples) + 1)
            ]
            self.vector_store.delete_points(ids)
            
            # Delete from local storage
            del self.patterns[pattern_id]
            self._save_patterns()
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to delete pattern: {e}")

    async def clear(self):
        """Clear all patterns."""
        try:
            self.vector_store.clear_collection()
            self.patterns = {}
            self._save_patterns()
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to clear patterns: {e}")
