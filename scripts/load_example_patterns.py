#!/usr/bin/env python3
"""Load example patterns into the knowledge base."""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.knowledge import KnowledgeBase, Pattern, PatternType, PatternConfidence
from mcp_codebase_insight.core.vector_store import VectorStore
from mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding

# Example patterns data
PATTERNS = [
    {
        "name": "Factory Method",
        "type": "design_pattern",
        "description": "Define an interface for creating an object, but let subclasses decide which class to instantiate.",
        "content": """
class Creator:
    def factory_method(self):
        pass
    
    def operation(self):
        product = self.factory_method()
        return product.operation()

class ConcreteCreator(Creator):
    def factory_method(self):
        return ConcreteProduct()
        """,
        "tags": ["creational", "factory", "object-creation"],
        "confidence": "high"
    },
    {
        "name": "Repository Pattern",
        "type": "architecture",
        "description": "Mediates between the domain and data mapping layers using a collection-like interface for accessing domain objects.",
        "content": """
class Repository:
    def get(self, id: str) -> Entity:
        pass
    
    def add(self, entity: Entity):
        pass
    
    def remove(self, entity: Entity):
        pass
        """,
        "tags": ["data-access", "persistence", "domain-driven-design"],
        "confidence": "high"
    },
    {
        "name": "Strategy Pattern",
        "type": "design_pattern",
        "description": "Define a family of algorithms, encapsulate each one, and make them interchangeable.",
        "content": """
class Strategy:
    def execute(self, data):
        pass

class ConcreteStrategyA(Strategy):
    def execute(self, data):
        return "Algorithm A"

class Context:
    def __init__(self, strategy: Strategy):
        self._strategy = strategy
    
    def execute_strategy(self, data):
        return self._strategy.execute(data)
        """,
        "tags": ["behavioral", "algorithm", "encapsulation"],
        "confidence": "high"
    },
    {
        "name": "Error Handling Pattern",
        "type": "code",
        "description": "Common pattern for handling errors in Python using try-except with context.",
        "content": """
def operation_with_context():
    try:
        # Setup resources
        resource = setup_resource()
        try:
            # Main operation
            result = process_resource(resource)
            return result
        except SpecificError as e:
            # Handle specific error
            handle_specific_error(e)
            raise
        finally:
            # Cleanup
            cleanup_resource(resource)
    except Exception as e:
        # Log error with context
        logger.error("Operation failed", exc_info=e)
        raise OperationError("Operation failed") from e
        """,
        "tags": ["error-handling", "python", "best-practice"],
        "confidence": "high"
    },
    {
        "name": "Circuit Breaker",
        "type": "architecture",
        "description": "Prevent system failure by failing fast and handling recovery.",
        "content": """
class CircuitBreaker:
    def __init__(self, failure_threshold, reset_timeout):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = None
        self.state = "closed"
    
    async def call(self, func, *args, **kwargs):
        if self._should_open():
            self.state = "open"
            raise CircuitBreakerOpen()
            
        try:
            result = await func(*args, **kwargs)
            self._reset()
            return result
        except Exception as e:
            self._record_failure()
            raise
        """,
        "tags": ["resilience", "fault-tolerance", "microservices"],
        "confidence": "high"
    }
]

async def main():
    """Load patterns into knowledge base."""
    try:
        # Create config
        config = ServerConfig()
        
        # Initialize components
        embedder = SentenceTransformerEmbedding(config.embedding_model)
        vector_store = VectorStore(
            url=config.qdrant_url,
            embedder=embedder,
            collection_name=config.collection_name
        )
        kb = KnowledgeBase(config, vector_store)
        
        # Create patterns directory if it doesn't exist
        patterns_dir = Path("knowledge/patterns")
        patterns_dir.mkdir(parents=True, exist_ok=True)
        
        # Load each pattern
        for pattern_data in PATTERNS:
            pattern = Pattern(
                name=pattern_data["name"],
                type=PatternType(pattern_data["type"]),
                description=pattern_data["description"],
                content=pattern_data["content"],
                tags=pattern_data["tags"],
                confidence=PatternConfidence(pattern_data["confidence"])
            )
            
            # Save pattern to knowledge base
            created = await kb.add_pattern(pattern)
            print(f"Added pattern: {created.name}")
            
            # Save pattern to file
            pattern_file = patterns_dir / f"{created.id}.json"
            with open(pattern_file, "w") as f:
                json.dump({
                    "id": created.id,
                    "name": created.name,
                    "type": created.type.value,
                    "description": created.description,
                    "content": created.content,
                    "tags": created.tags,
                    "confidence": created.confidence.value,
                    "created_at": datetime.now().isoformat()
                }, f, indent=2)
        
        print("\nAll patterns loaded successfully!")
        
        # Test search
        print("\nTesting pattern search...")
        results = await kb.find_similar_patterns(
            "error handling in Python",
            limit=2
        )
        
        print("\nSearch results:")
        for result in results:
            print(f"- {result.name} (score: {result.similarity_score:.2f})")
        
    except Exception as e:
        print(f"Error loading patterns: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
