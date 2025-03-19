#!/usr/bin/env python3
"""Load example patterns into the knowledge base."""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_server_qdrant.core.config import ServerConfig
from mcp_server_qdrant.core.embeddings import EmbeddingProvider
from mcp_server_qdrant.core.vector_store import VectorStore
from mcp_server_qdrant.core.knowledge import KnowledgeBase, PatternType
from mcp_server_qdrant.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

# Example patterns
PATTERNS = [
    # Code patterns
    {
        "type": PatternType.CODE,
        "name": "Repository Structure",
        "description": "Standard repository structure for Python projects",
        "content": """
A well-organized Python project should follow this structure:
```
project_name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── core/
│       ├── utils/
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── Makefile
```
""",
        "examples": [
            "https://github.com/psf/black",
            "https://github.com/pallets/flask"
        ],
        "context": {
            "language": "python",
            "domain": "project_structure"
        },
        "tags": ["python", "repository", "structure", "organization"]
    },
    
    # Architecture patterns
    {
        "type": PatternType.ARCHITECTURE,
        "name": "Clean Architecture",
        "description": "Implementation of Clean Architecture in Python",
        "content": """
Clean Architecture layers:
1. Entities (core business objects)
2. Use Cases (application business rules)
3. Interface Adapters (controllers, presenters)
4. Frameworks & Drivers (external interfaces)

Key principles:
- Dependencies point inward
- Inner layers know nothing about outer layers
- Business rules isolated from UI/database
""",
        "examples": [
            "https://github.com/jasongoodwin/clean-architecture-example",
            "https://github.com/ardanlabs/service"
        ],
        "context": {
            "domain": "architecture",
            "paradigm": "clean_architecture"
        },
        "tags": ["architecture", "clean", "dependency-rule", "solid"]
    },
    
    # Debug patterns
    {
        "type": PatternType.DEBUG,
        "name": "Systematic Debugging",
        "description": "Systematic approach to debugging using Agans' 9 Rules",
        "content": """
1. Understand the system
2. Make it fail
3. Quit thinking and look
4. Divide and conquer
5. Change one thing at a time
6. Keep an audit trail
7. Check the plug
8. Get a fresh view
9. If you didn't fix it, it ain't fixed
""",
        "examples": [
            "Example: Memory leak investigation",
            "Example: Race condition debugging"
        ],
        "context": {
            "domain": "debugging",
            "methodology": "systematic"
        },
        "tags": ["debug", "methodology", "systematic", "agans-rules"]
    },
    
    # Solution patterns
    {
        "type": PatternType.SOLUTION,
        "name": "Dependency Injection",
        "description": "Implementation of dependency injection pattern",
        "content": """
Key components:
1. Service interface
2. Service implementation
3. Service consumer
4. Injector

Benefits:
- Decoupled components
- Easier testing
- Flexible configuration
- Maintainable code
""",
        "examples": [
            "Example: Database connection injection",
            "Example: Configuration service injection"
        ],
        "context": {
            "domain": "design_patterns",
            "pattern_type": "dependency_injection"
        },
        "tags": ["design-pattern", "dependency-injection", "solid"]
    },
    
    # Best practice patterns
    {
        "type": PatternType.BEST_PRACTICE,
        "name": "Error Handling",
        "description": "Best practices for error handling in Python",
        "content": """
1. Use custom exceptions for domain errors
2. Catch specific exceptions
3. Provide context in error messages
4. Log errors with stack traces
5. Clean up resources in finally blocks
6. Use context managers (with statement)
7. Return early for error conditions
8. Validate input at boundaries
""",
        "examples": [
            "Example: Custom exception hierarchy",
            "Example: Context manager implementation"
        ],
        "context": {
            "language": "python",
            "domain": "error_handling"
        },
        "tags": ["python", "error-handling", "exceptions", "best-practices"]
    }
]

async def main():
    """Load example patterns into knowledge base."""
    # Setup logging
    setup_logging("INFO")
    
    # Load config
    config = ServerConfig.from_env()
    
    # Initialize components
    client = QdrantClient(url=config.qdrant_url)
    embedder = await EmbeddingProvider.create(config)
    vector_store = VectorStore(client, embedder, config.collection_name)
    knowledge_base = KnowledgeBase(config, vector_store)
    
    # Initialize vector store
    await vector_store.initialize()
    
    # Store patterns
    logger.info("Loading example patterns...")
    for pattern in PATTERNS:
        try:
            await knowledge_base.store_pattern(
                type=pattern["type"],
                name=pattern["name"],
                description=pattern["description"],
                content=pattern["content"],
                examples=pattern["examples"],
                context=pattern["context"],
                tags=set(pattern["tags"])
            )
            logger.info(f"Stored pattern: {pattern['name']}")
        except Exception as e:
            logger.error(f"Error storing pattern {pattern['name']}: {e}")
    
    logger.info("Finished loading example patterns")

if __name__ == "__main__":
    asyncio.run(main())
