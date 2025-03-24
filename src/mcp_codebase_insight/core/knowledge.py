"""Knowledge base for code patterns and insights."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import json

from pydantic import BaseModel, Field

class PatternType(str, Enum):
    """Pattern type enumeration."""
    
    CODE = "code"
    DESIGN_PATTERN = "design_pattern"
    ARCHITECTURE = "architecture"
    BEST_PRACTICE = "best_practice"
    ANTI_PATTERN = "anti_pattern"
    FILE_RELATIONSHIP = "file_relationship"  # New type for file relationships
    WEB_SOURCE = "web_source"  # New type for web sources

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

class FileRelationship(BaseModel):
    """File relationship model."""
    
    source_file: str
    target_file: str
    relationship_type: str  # e.g., "imports", "extends", "implements", "uses"
    description: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WebSource(BaseModel):
    """Web source model."""
    
    url: str
    title: str
    description: Optional[str] = None
    content_type: str  # e.g., "documentation", "tutorial", "reference"
    last_fetched: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, str]] = None
    related_patterns: Optional[List[UUID]] = None
    tags: Optional[List[str]] = None

class KnowledgeBase:
    """Knowledge base for managing code patterns and insights."""
    
    def __init__(self, config, vector_store=None):
        """Initialize knowledge base.
        
        Args:
            config: Server configuration
            vector_store: Optional vector store instance
        """
        self.config = config
        self.vector_store = vector_store
        self.kb_dir = config.kb_storage_dir
        self.initialized = False
        self.file_relationships: Dict[str, FileRelationship] = {}
        self.web_sources: Dict[str, WebSource] = {}
    
    async def initialize(self):
        """Initialize knowledge base components."""
        if self.initialized:
            return
            
        try:
            # Create all required directories
            self.kb_dir.mkdir(parents=True, exist_ok=True)
            (self.kb_dir / "patterns").mkdir(parents=True, exist_ok=True)
            (self.kb_dir / "relationships").mkdir(parents=True, exist_ok=True)  # New directory for relationships
            (self.kb_dir / "web_sources").mkdir(parents=True, exist_ok=True)  # New directory for web sources
            
            # Initialize vector store if available
            if self.vector_store:
                await self.vector_store.initialize()
                
            # Load existing relationships and web sources
            await self._load_relationships()
            await self._load_web_sources()
                
            # Create initial patterns if none exist
            if not list((self.kb_dir / "patterns").glob("*.json")):
                await self._create_initial_patterns()
                
            # Update state
            self.config.set_state("kb_initialized", True)
            self.initialized = True
        except Exception as e:
            import traceback
            print(f"Error initializing knowledge base: {str(e)}\n{traceback.format_exc()}")
            self.config.set_state("kb_initialized", False)
            self.config.set_state("kb_error", str(e))
            raise RuntimeError(f"Failed to initialize knowledge base: {str(e)}")
    
    async def _load_relationships(self):
        """Load existing file relationships."""
        relationships_dir = self.kb_dir / "relationships"
        if relationships_dir.exists():
            for file_path in relationships_dir.glob("*.json"):
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        relationship = FileRelationship(**data)
                        key = f"{relationship.source_file}:{relationship.target_file}"
                        self.file_relationships[key] = relationship
                except Exception as e:
                    print(f"Error loading relationship from {file_path}: {e}")
    
    async def _load_web_sources(self):
        """Load existing web sources."""
        web_sources_dir = self.kb_dir / "web_sources"
        if web_sources_dir.exists():
            for file_path in web_sources_dir.glob("*.json"):
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        source = WebSource(**data)
                        self.web_sources[source.url] = source
                except Exception as e:
                    print(f"Error loading web source from {file_path}: {e}")
    
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
        if not self.initialized:
            return
            
        try:
            if self.vector_store:
                await self.vector_store.cleanup()
        except Exception as e:
            print(f"Error cleaning up knowledge base: {e}")
        finally:
            self.config.set_state("kb_initialized", False)
            self.initialized = False
    
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
            # Generate embedding for the pattern
            combined_text = f"{pattern.name}\n{pattern.description}\n{pattern.content}"
            embedding = await self.vector_store.embedder.embed(combined_text)
            
            await self.vector_store.store_pattern(
                pattern_id=str(pattern.id),
                title=pattern.name,
                description=pattern.description,
                pattern_type=pattern.type.value,
                tags=pattern.tags or [],
                embedding=embedding
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
            # Generate embedding for the updated pattern
            combined_text = f"{pattern.name}\n{pattern.description}\n{pattern.content}"
            embedding = await self.vector_store.embedder.embed(combined_text)
            
            # Update pattern with embedding
            await self.vector_store.update_pattern(
                pattern_id=str(pattern.id),
                title=pattern.name,
                description=pattern.description,
                pattern_type=pattern.type.value,
                tags=pattern.tags or [],
                embedding=embedding
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
    
    async def analyze_code(self, code: str, context: Optional[Dict[str, str]] = None) -> Dict:
        """Analyze code for patterns and insights.
        
        Args:
            code: The code to analyze.
            context: Optional context about the code, such as language and purpose.
        """
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
                "total_insights": len(insights),
                "context": context or {}
            }
        }
    
    async def _save_pattern(self, pattern: Pattern) -> None:
        """Save pattern to file."""
        pattern_dir = self.kb_dir / "patterns"
        pattern_dir.mkdir(parents=True, exist_ok=True)
        pattern_path = pattern_dir / f"{pattern.id}.json"
        with open(pattern_path, "w") as f:
            json.dump(pattern.dict(), f, indent=2, default=str)

    async def search_patterns(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """Search for patterns using text query."""
        try:
            # Convert pattern_type string to enum if provided
            pattern_type_enum = None
            if pattern_type:
                try:
                    pattern_type_enum = PatternType(pattern_type)
                except ValueError:
                    pass  # Invalid pattern type, will be ignored
            
            # Use find_similar_patterns with the converted type
            return await self.find_similar_patterns(
                query=query,
                pattern_type=pattern_type_enum,
                limit=limit
            )
        except Exception as e:
            print(f"Error searching patterns: {str(e)}")
            return []

    async def add_file_relationship(
        self,
        source_file: str,
        target_file: str,
        relationship_type: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> FileRelationship:
        """Add a new file relationship."""
        relationship = FileRelationship(
            source_file=source_file,
            target_file=target_file,
            relationship_type=relationship_type,
            description=description,
            metadata=metadata
        )
        
        key = f"{source_file}:{target_file}"
        self.file_relationships[key] = relationship
        
        # Save to disk
        await self._save_relationship(relationship)
        return relationship
    
    async def add_web_source(
        self,
        url: str,
        title: str,
        content_type: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None
    ) -> WebSource:
        """Add a new web source."""
        source = WebSource(
            url=url,
            title=title,
            content_type=content_type,
            description=description,
            metadata=metadata,
            tags=tags
        )
        
        self.web_sources[url] = source
        
        # Save to disk
        await self._save_web_source(source)
        return source
    
    async def get_file_relationships(
        self,
        source_file: Optional[str] = None,
        target_file: Optional[str] = None,
        relationship_type: Optional[str] = None
    ) -> List[FileRelationship]:
        """Get file relationships, optionally filtered."""
        relationships = list(self.file_relationships.values())
        
        if source_file:
            relationships = [r for r in relationships if r.source_file == source_file]
        if target_file:
            relationships = [r for r in relationships if r.target_file == target_file]
        if relationship_type:
            relationships = [r for r in relationships if r.relationship_type == relationship_type]
            
        return relationships
    
    async def get_web_sources(
        self,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[WebSource]:
        """Get web sources, optionally filtered."""
        sources = list(self.web_sources.values())
        
        if content_type:
            sources = [s for s in sources if s.content_type == content_type]
        if tags:
            sources = [s for s in sources if s.tags and all(tag in s.tags for tag in tags)]
            
        return sources
    
    async def _save_relationship(self, relationship: FileRelationship) -> None:
        """Save file relationship to disk."""
        relationships_dir = self.kb_dir / "relationships"
        relationships_dir.mkdir(parents=True, exist_ok=True)
        
        key = f"{relationship.source_file}:{relationship.target_file}"
        file_path = relationships_dir / f"{hash(key)}.json"
        
        with open(file_path, "w") as f:
            json.dump(relationship.model_dump(), f, indent=2, default=str)
    
    async def _save_web_source(self, source: WebSource) -> None:
        """Save web source to disk."""
        web_sources_dir = self.kb_dir / "web_sources"
        web_sources_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = web_sources_dir / f"{hash(source.url)}.json"
        
        with open(file_path, "w") as f:
            json.dump(source.model_dump(), f, indent=2, default=str)
