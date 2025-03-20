"""Knowledge base for code patterns and insights."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import json

from pydantic import BaseModel

class PatternType(str, Enum):
    """Pattern type enumeration."""
    
    CODE = "code"
    DESIGN_PATTERN = "design_pattern"
    ARCHITECTURE = "architecture"
    BEST_PRACTICE = "best_practice"
    ANTI_PATTERN = "anti_pattern"

class PatternConfidence(str, Enum):
    """Pattern confidence level."""
    
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EXPERIMENTAL = "experimental"

class Pattern(BaseModel):
    """Pattern model."""
    
    id: UUID
    name: str
    type: PatternType
    description: str
    content: str
    confidence: PatternConfidence
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, str]] = None
    created_at: datetime
    updated_at: datetime
    examples: Optional[List[str]] = None
    related_patterns: Optional[List[UUID]] = None

class SearchResult(BaseModel):
    """Pattern search result model."""
    
    pattern: Pattern
    similarity_score: float

class KnowledgeBase:
    """Knowledge base for managing code patterns and insights."""
    
    def __init__(self, config, vector_store=None):
        """Initialize knowledge base."""
        self.config = config
        self.vector_store = vector_store
        self.kb_dir = config.kb_storage_dir
        # Create all required directories
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        (self.kb_dir / "patterns").mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize knowledge base components."""
        try:
            if self.vector_store:
                await self.vector_store.initialize()
            # Create initial patterns if none exist
            if not list((self.kb_dir / "patterns").glob("*.json")):
                await self._create_initial_patterns()
        except Exception as e:
            import traceback
            print(f"Error initializing knowledge base: {str(e)}\n{traceback.format_exc()}")
            raise RuntimeError(f"Failed to initialize knowledge base: {str(e)}")
    
    async def _create_initial_patterns(self):
        """Create initial patterns for testing."""
        await self.add_pattern(
            name="Basic Function",
            type=PatternType.CODE,
            description="A simple function that performs a calculation",
            content="def calculate(x, y):\n    return x + y",
            confidence=PatternConfidence.HIGH,
            tags=["function", "basic"]
        )
    
    async def cleanup(self):
        """Clean up knowledge base components."""
        if self.vector_store:
            await self.vector_store.cleanup()
    
    async def add_pattern(
        self,
        name: str,
        type: PatternType,
        description: str,
        content: str,
        confidence: PatternConfidence,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        examples: Optional[List[str]] = None,
        related_patterns: Optional[List[UUID]] = None
    ) -> Pattern:
        """Add a new pattern."""
        now = datetime.utcnow()
        pattern = Pattern(
            id=uuid4(),
            name=name,
            type=type,
            description=description,
            content=content,
            confidence=confidence,
            tags=tags,
            metadata=metadata,
            examples=examples,
            related_patterns=related_patterns,
            created_at=now,
            updated_at=now
        )
        
        # Store pattern vector if vector store is available
        if self.vector_store:
            await self.vector_store.store_pattern(
                id=str(pattern.id),
                text=f"{pattern.name}\n{pattern.description}\n{pattern.content}",
                metadata={
                    "type": pattern.type,
                    "confidence": pattern.confidence,
                    "tags": pattern.tags or []
                }
            )
        
        # Save pattern to file
        await self._save_pattern(pattern)
        return pattern
    
    async def get_pattern(self, pattern_id: UUID) -> Optional[Pattern]:
        """Get pattern by ID."""
        pattern_path = self.kb_dir / "patterns" / f"{pattern_id}.json"
        if not pattern_path.exists():
            return None
            
        with open(pattern_path) as f:
            data = json.load(f)
            return Pattern(**data)
    
    async def update_pattern(
        self,
        pattern_id: UUID,
        description: Optional[str] = None,
        content: Optional[str] = None,
        confidence: Optional[PatternConfidence] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        examples: Optional[List[str]] = None,
        related_patterns: Optional[List[UUID]] = None
    ) -> Optional[Pattern]:
        """Update pattern details."""
        pattern = await self.get_pattern(pattern_id)
        if not pattern:
            return None
            
        if description:
            pattern.description = description
        if content:
            pattern.content = content
        if confidence:
            pattern.confidence = confidence
        if tags:
            pattern.tags = tags
        if metadata:
            pattern.metadata = {**(pattern.metadata or {}), **metadata}
        if examples:
            pattern.examples = examples
        if related_patterns:
            pattern.related_patterns = related_patterns
            
        pattern.updated_at = datetime.utcnow()
        
        # Update vector store if available
        if self.vector_store:
            await self.vector_store.update_pattern(
                id=str(pattern.id),
                text=f"{pattern.name}\n{pattern.description}\n{pattern.content}",
                metadata={
                    "type": pattern.type,
                    "confidence": pattern.confidence,
                    "tags": pattern.tags or []
                }
            )
        
        await self._save_pattern(pattern)
        return pattern
    
    async def find_similar_patterns(
        self,
        query: str,
        pattern_type: Optional[PatternType] = None,
        confidence: Optional[PatternConfidence] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """Find similar patterns using vector similarity search."""
        if not self.vector_store:
            return []
            
        # Build filter conditions
        filter_conditions = {}
        if pattern_type:
            filter_conditions["type"] = pattern_type
        if confidence:
            filter_conditions["confidence"] = confidence
        if tags:
            filter_conditions["tags"] = {"$all": tags}
            
        # Search vectors
        results = await self.vector_store.search(
            text=query,
            filter_conditions=filter_conditions,
            limit=limit
        )
        
        # Load full patterns
        search_results = []
        for result in results:
            pattern = await self.get_pattern(UUID(result.id))
            if pattern:
                search_results.append(SearchResult(
                    pattern=pattern,
                    similarity_score=result.score
                ))
                
        return search_results
    
    async def list_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        confidence: Optional[PatternConfidence] = None,
        tags: Optional[List[str]] = None
    ) -> List[Pattern]:
        """List all patterns, optionally filtered."""
        patterns = []
        for path in (self.kb_dir / "patterns").glob("*.json"):
            with open(path) as f:
                data = json.load(f)
                pattern = Pattern(**data)
                
                # Apply filters
                if pattern_type and pattern.type != pattern_type:
                    continue
                if confidence and pattern.confidence != confidence:
                    continue
                if tags and not all(tag in (pattern.tags or []) for tag in tags):
                    continue
                    
                patterns.append(pattern)
                
        return sorted(patterns, key=lambda x: x.created_at)
    
    async def analyze_code(self, code: str) -> Dict:
        """Analyze code for patterns and insights."""
        # Find similar code patterns
        patterns = await self.find_similar_patterns(
            query=code,
            pattern_type=PatternType.CODE,
            limit=5
        )
        
        # Extract insights
        insights = []
        for result in patterns:
            pattern = result.pattern
            insights.append({
                "pattern_id": str(pattern.id),
                "name": pattern.name,
                "description": pattern.description,
                "confidence": pattern.confidence,
                "similarity_score": result.similarity_score
            })
            
        return {
            "patterns": [p.pattern.dict() for p in patterns],
            "insights": insights,
            "summary": {
                "total_patterns": len(patterns),
                "total_insights": len(insights)
            }
        }
    
    async def _save_pattern(self, pattern: Pattern) -> None:
        """Save pattern to file."""
        pattern_dir = self.kb_dir / "patterns"
        pattern_dir.mkdir(parents=True, exist_ok=True)
        pattern_path = pattern_dir / f"{pattern.id}.json"
        with open(pattern_path, "w") as f:
            json.dump(pattern.dict(), f, indent=2, default=str)
