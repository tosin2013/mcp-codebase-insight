#!/usr/bin/env python3
"""Load example patterns and ADRs into the knowledge base."""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.knowledge import KnowledgeBase, Pattern, PatternType, PatternConfidence
from mcp_codebase_insight.core.vector_store import VectorStore
from mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding
from mcp_codebase_insight.core.adr import ADRManager, ADRStatus

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

# Example ADRs data
ADRS = [
    {
        "title": "Use FastAPI for REST API Development",
        "context": {
            "problem": "We need a modern, high-performance web framework for our REST API",
            "constraints": [
                "Must support Python 3.9+",
                "Must support async/await",
                "Must have strong type validation",
                "Must have good documentation"
            ],
            "assumptions": [
                "The team has Python experience",
                "Performance is a priority"
            ]
        },
        "options": [
            {
                "title": "Use Flask",
                "pros": [
                    "Simple and familiar",
                    "Large ecosystem",
                    "Easy to learn"
                ],
                "cons": [
                    "No built-in async support",
                    "No built-in validation",
                    "Requires many extensions"
                ]
            },
            {
                "title": "Use FastAPI",
                "pros": [
                    "Built-in async support",
                    "Automatic OpenAPI documentation",
                    "Built-in validation with Pydantic",
                    "High performance"
                ],
                "cons": [
                    "Newer framework with smaller ecosystem",
                    "Steeper learning curve for some concepts"
                ]
            },
            {
                "title": "Use Django REST Framework",
                "pros": [
                    "Mature and stable",
                    "Full-featured",
                    "Large community"
                ],
                "cons": [
                    "Heavier weight",
                    "Limited async support",
                    "Slower than alternatives"
                ]
            }
        ],
        "decision": "We will use FastAPI for our REST API development due to its modern features, performance, and built-in support for async/await and validation.",
        "consequences": {
            "positive": [
                "Improved API performance",
                "Better developer experience with type hints and validation",
                "Automatic API documentation"
            ],
            "negative": [
                "Team needs to learn new concepts (dependency injection, Pydantic)",
                "Fewer third-party extensions compared to Flask or Django"
            ]
        }
    },
    {
        "title": "Vector Database for Semantic Search",
        "context": {
            "problem": "We need a database solution for storing and searching vector embeddings for semantic code search",
            "constraints": [
                "Must support efficient vector similarity search",
                "Must scale to handle large codebases",
                "Must be easy to integrate with Python"
            ]
        },
        "options": [
            {
                "title": "Use Qdrant",
                "pros": [
                    "Purpose-built for vector search",
                    "Good Python client",
                    "Fast similarity search",
                    "Support for filters"
                ],
                "cons": [
                    "Relatively new project",
                    "Limited community compared to alternatives"
                ]
            },
            {
                "title": "Use Elasticsearch with vector capabilities",
                "pros": [
                    "Mature product",
                    "Well-known in industry",
                    "Many features beyond vector search"
                ],
                "cons": [
                    "More complex to set up",
                    "Not optimized exclusively for vector search",
                    "Higher resource requirements"
                ]
            },
            {
                "title": "Build custom solution with NumPy/FAISS",
                "pros": [
                    "Complete control over implementation",
                    "No external service dependency",
                    "Can optimize for specific needs"
                ],
                "cons": [
                    "Significant development effort",
                    "Need to handle persistence manually",
                    "Maintenance burden"
                ]
            }
        ],
        "decision": "We will use Qdrant for vector storage and similarity search due to its performance, ease of use, and purpose-built design for vector operations.",
        "consequences": {
            "positive": [
                "Fast similarity search with minimal setup",
                "Simple API for vector operations",
                "Good scalability as codebase grows"
            ],
            "negative": [
                "New dependency to maintain",
                "Team needs to learn Qdrant-specific concepts"
            ]
        }
    }
]

async def main():
    """Load patterns and ADRs into knowledge base."""
    try:
        # Create config
        config = ServerConfig()
        
        # Initialize components
        embedder = SentenceTransformerEmbedding(config.embedding_model)
        vector_store = VectorStore(
            url=config.qdrant_url,
            embedder=embedder,
            collection_name=config.collection_name,
            vector_name="fast-all-minilm-l6-v2"
        )
        
        # Initialize vector store
        await vector_store.initialize()
        
        # Create knowledge base
        kb = KnowledgeBase(config, vector_store)
        await kb.initialize()
        
        # Create patterns directory if it doesn't exist
        patterns_dir = Path("knowledge/patterns")
        patterns_dir.mkdir(parents=True, exist_ok=True)
        
        # Create ADRs directory if it doesn't exist
        adrs_dir = Path("docs/adrs")
        adrs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load each pattern
        print("\n=== Loading Patterns ===")
        for pattern_data in PATTERNS:
            # Save pattern to knowledge base using the correct method signature
            created = await kb.add_pattern(
                name=pattern_data["name"],
                type=PatternType(pattern_data["type"]),
                description=pattern_data["description"],
                content=pattern_data["content"],
                confidence=PatternConfidence(pattern_data["confidence"]),
                tags=pattern_data["tags"]
            )
            
            print(f"Added pattern: {created.name}")
            
            # Save pattern to file
            pattern_file = patterns_dir / f"{created.id}.json"
            with open(pattern_file, "w") as f:
                json.dump({
                    "id": str(created.id),
                    "name": created.name,
                    "type": created.type.value,
                    "description": created.description,
                    "content": created.content,
                    "tags": created.tags,
                    "confidence": created.confidence.value,
                    "created_at": created.created_at.isoformat(),
                    "updated_at": created.updated_at.isoformat()
                }, f, indent=2)
        
        print("\nAll patterns loaded successfully!")
        
        # Initialize ADR manager
        print("\n=== Loading ADRs ===")
        adr_manager = ADRManager(config)
        await adr_manager.initialize()
        
        # Load each ADR
        for adr_data in ADRS:
            created = await adr_manager.create_adr(
                title=adr_data["title"],
                context=adr_data["context"],
                options=adr_data["options"],
                decision=adr_data["decision"],
                consequences=adr_data.get("consequences")
            )
            
            print(f"Added ADR: {created.title}")
        
        print("\nAll ADRs loaded successfully!")
        
        # Test pattern search
        print("\n=== Testing Pattern Search ===")
        results = await kb.find_similar_patterns(
            "error handling in Python",
            limit=2
        )
        
        print("\nSearch results:")
        for result in results:
            print(f"- {result.pattern.name} (score: {result.similarity_score:.2f})")
            
        # Test ADR listing
        print("\n=== Testing ADR Listing ===")
        adrs = await adr_manager.list_adrs()
        
        print(f"\nFound {len(adrs)} ADRs:")
        for adr in adrs:
            print(f"- {adr.title} (status: {adr.status})")
        
    except Exception as e:
        print(f"Error loading examples: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
