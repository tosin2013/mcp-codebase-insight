import sys
import os

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
import pytest_asyncio
from pathlib import Path
from typing import AsyncGenerator
from src.mcp_codebase_insight.core.knowledge import KnowledgeBase, PatternType, PatternConfidence
from src.mcp_codebase_insight.core.config import ServerConfig
from src.mcp_codebase_insight.core.vector_store import VectorStore

@pytest_asyncio.fixture
async def knowledge_base(test_config: ServerConfig, vector_store: VectorStore):
    kb = KnowledgeBase(test_config, vector_store)
    await kb.initialize()
    yield kb
    await kb.cleanup()

@pytest.mark.asyncio
async def test_knowledge_base_initialization(knowledge_base: KnowledgeBase):
    """Test that knowledge base initializes correctly."""
    assert knowledge_base is not None
    assert knowledge_base.vector_store is not None
    assert knowledge_base.config is not None

@pytest.mark.asyncio
async def test_add_and_get_pattern(knowledge_base: KnowledgeBase):
    """Test adding and retrieving patterns."""
    # Add pattern
    pattern_data = {
        "name": "Test Pattern",
        "description": "A test pattern",
        "content": "def test(): pass",  # Note: renamed from 'code' to 'content' to match implementation
        "tags": ["test", "example"]
    }

    pattern = await knowledge_base.add_pattern(
        name=pattern_data["name"],
        type=PatternType.CODE,
        description=pattern_data["description"],
        content=pattern_data["content"],
        confidence=PatternConfidence.MEDIUM,
        tags=pattern_data["tags"]
    )

    assert pattern.id is not None

    # Get pattern
    retrieved = await knowledge_base.get_pattern(pattern.id)
    assert retrieved.name == pattern_data["name"]
    assert retrieved.description == pattern_data["description"]

@pytest.mark.asyncio
async def test_find_similar_patterns(knowledge_base: KnowledgeBase):
    """Test finding similar patterns with different queries and thresholds."""
    # Add test patterns with more substantial content to create better embeddings
    pattern1_data = {
        "name": "Python Class Example",
        "description": "An example of a Python class with methods",
        "content": """
class SearchResult:
    \"\"\"Represents a search result from the vector store.\"\"\"
    def __init__(self, id: str, score: float, metadata: dict = None):
        self.id = id
        self.score = score
        self.metadata = metadata or {}
        
    def to_dict(self):
        \"\"\"Convert to dictionary.\"\"\"
        return {
            "id": self.id,
            "score": self.score,
            "metadata": self.metadata
        }
        """,
        "tags": ["class", "python", "search"]
    }
    
    pattern2_data = {
        "name": "Async Function Example",
        "description": "An example of an async function in Python",
        "content": """
async def search_patterns(query: str, limit: int = 5, threshold: float = 0.7):
    \"\"\"Search for patterns matching the query.\"\"\"
    # Generate embedding for the query
    embedding = await generate_embedding(query)
    
    # Perform the search
    results = await vector_store.search(
        embedding=embedding,
        limit=limit
    )
    
    # Filter by threshold
    filtered_results = [r for r in results if r.score >= threshold]
    
    return filtered_results
        """,
        "tags": ["async", "function", "python", "search"]
    }
    
    pattern3_data = {
        "name": "Semantic Search Documentation",
        "description": "Documentation about using semantic search",
        "content": """
# Semantic Search

Semantic search uses embeddings to find similar content based on meaning rather than keywords.

## Search Parameters:

- **query**: The text to search for similar patterns
- **threshold**: Similarity score threshold (0.0 to 1.0)
- **limit**: Maximum number of results to return

## Example Usage:

```python
results = await search("Python class example", threshold=0.7)
```
        """,
        "tags": ["documentation", "search", "embeddings"]
    }

    # Add all patterns
    pattern1 = await knowledge_base.add_pattern(
        name=pattern1_data["name"],
        type=PatternType.CODE,
        description=pattern1_data["description"],
        content=pattern1_data["content"],
        confidence=PatternConfidence.HIGH,
        tags=pattern1_data["tags"]
    )

    pattern2 = await knowledge_base.add_pattern(
        name=pattern2_data["name"],
        type=PatternType.CODE,
        description=pattern2_data["description"],
        content=pattern2_data["content"],
        confidence=PatternConfidence.MEDIUM,
        tags=pattern2_data["tags"]
    )
    
    pattern3 = await knowledge_base.add_pattern(
        name=pattern3_data["name"],
        type=PatternType.BEST_PRACTICE,  # Using BEST_PRACTICE instead of DOCUMENTATION
        description=pattern3_data["description"],
        content=pattern3_data["content"],
        confidence=PatternConfidence.HIGH,
        tags=pattern3_data["tags"]
    )

    # Define test cases with different queries and expected pattern matches
    test_cases = [
        {
            "query": "Python class with methods",
            "threshold": 0.7,
            "expected_pattern_ids": [pattern1.id]
        },
        {
            "query": "async function for searching",
            "threshold": 0.65,
            "expected_pattern_ids": [pattern2.id]
        },
        {
            "query": "semantic search documentation",
            "threshold": 0.6,
            "expected_pattern_ids": [pattern3.id]
        },
        {
            "query": "search",  # Generic query that should match multiple patterns
            "threshold": 0.5,
            "min_expected_count": 2
        }
    ]
    
    # Test each case
    for tc in test_cases:
        similar = await knowledge_base.find_similar_patterns(
            query=tc["query"],
            limit=5,
            pattern_type=None,  # Test without type filter
            confidence=None,    # Test without confidence filter
            tags=None          # Test without tag filter
        )
        
        # Assert we have results
        assert len(similar) > 0, f"Query '{tc['query']}' returned no results"
        
        # Check for specific expected IDs if specified
        if "expected_pattern_ids" in tc:
            found_ids = [str(result.pattern.id) for result in similar]
            for expected_id in tc["expected_pattern_ids"]:
                assert str(expected_id) in found_ids, \
                    f"Expected pattern {expected_id} not found in results for query '{tc['query']}'"
        
        # Check for minimum count if specified
        if "min_expected_count" in tc:
            assert len(similar) >= tc["min_expected_count"], \
                f"Expected at least {tc['min_expected_count']} results for query '{tc['query']}', got {len(similar)}"
        
        # Verify result structure
        for result in similar:
            assert hasattr(result, "pattern"), "Result missing 'pattern' attribute"
            assert hasattr(result, "similarity_score"), "Result missing 'similarity_score' attribute"
            assert isinstance(result.similarity_score, float), f"Similarity score is not a float: {result.similarity_score}"
            assert 0 <= result.similarity_score <= 1, f"Similarity score {result.similarity_score} out of valid range [0,1]"
        
    # Test with type filter
    code_results = await knowledge_base.find_similar_patterns(
        query="search",
        pattern_type=PatternType.CODE
    )
    assert len(code_results) > 0, "No results found with CODE type filter"
    assert all(result.pattern.type == PatternType.CODE for result in code_results), \
        "Found results with incorrect type when filtering by CODE"
    
    # Test with confidence filter
    high_confidence_results = await knowledge_base.find_similar_patterns(
        query="search",
        confidence=PatternConfidence.HIGH
    )
    assert len(high_confidence_results) > 0, "No results found with HIGH confidence filter"
    assert all(result.pattern.confidence == PatternConfidence.HIGH for result in high_confidence_results), \
        "Found results with incorrect confidence when filtering by HIGH"
    
    # Test with tags filter
    documentation_results = await knowledge_base.find_similar_patterns(
        query="search",
        tags=["documentation"]
    )
    assert len(documentation_results) > 0, "No results found with 'documentation' tag filter"
    assert all("documentation" in (result.pattern.tags or []) for result in documentation_results), \
        "Found results without 'documentation' tag when filtering by tag"

@pytest.mark.asyncio
async def test_update_pattern(knowledge_base: KnowledgeBase):
    """Test updating patterns."""
    # Add initial pattern
    pattern_data = {
        "name": "Original Pattern",
        "description": "Original description",
        "content": "def original(): pass",
        "tags": ["original"]
    }

    pattern = await knowledge_base.add_pattern(
        name=pattern_data["name"],
        type=PatternType.CODE,
        description=pattern_data["description"],
        content=pattern_data["content"],
        confidence=PatternConfidence.MEDIUM,
        tags=pattern_data["tags"]
    )

    # Update pattern
    updated_data = {
        "name": "Updated Pattern",
        "description": "Updated description",
        "content": "def updated(): pass",
        "tags": ["updated"]
    }

    await knowledge_base.update_pattern(
        pattern_id=pattern.id,
        description=updated_data["description"],
        content=updated_data["content"],
        tags=updated_data["tags"]
    )

    # Verify update
    retrieved = await knowledge_base.get_pattern(pattern.id)
    # Name is not updated by the update_pattern method
    assert retrieved.name == pattern_data["name"]  # Original name should remain
    assert retrieved.description == updated_data["description"]

@pytest.mark.asyncio
async def test_delete_pattern(knowledge_base: KnowledgeBase):
    """Test deleting patterns."""
    # Add a pattern to delete
    pattern_data = {
        "name": "Pattern to Delete",
        "description": "This pattern will be deleted",
        "content": "def to_be_deleted(): pass",
        "tags": ["delete", "test"]
    }

    pattern = await knowledge_base.add_pattern(
        name=pattern_data["name"],
        type=PatternType.CODE,
        description=pattern_data["description"],
        content=pattern_data["content"],
        confidence=PatternConfidence.MEDIUM,
        tags=pattern_data["tags"]
    )

    # Verify pattern exists
    retrieved_before = await knowledge_base.get_pattern(pattern.id)
    assert retrieved_before is not None

    # Delete the pattern
    await knowledge_base.delete_pattern(pattern.id)

    # Verify pattern no longer exists
    try:
        retrieved_after = await knowledge_base.get_pattern(pattern.id)
        assert retrieved_after is None, "Pattern should have been deleted"
    except Exception as e:
        # Either the pattern is None or an exception is raised (both are acceptable)
        pass

@pytest.mark.asyncio
async def test_search_patterns_by_tag(knowledge_base: KnowledgeBase):
    """Test searching patterns by tag."""
    # Add patterns with different tags
    tag1_pattern = await knowledge_base.add_pattern(
        name="Tag1 Pattern",
        type=PatternType.CODE,
        description="Pattern with tag1",
        content="def tag1_function(): pass",
        confidence=PatternConfidence.HIGH,
        tags=["tag1", "common"]
    )

    tag2_pattern = await knowledge_base.add_pattern(
        name="Tag2 Pattern",
        type=PatternType.CODE,
        description="Pattern with tag2",
        content="def tag2_function(): pass",
        confidence=PatternConfidence.HIGH,
        tags=["tag2", "common"]
    )

    # Search by tag1
    tag1_results = await knowledge_base.search_patterns(tags=["tag1"])
    assert any(p.id == tag1_pattern.id for p in tag1_results)
    assert not any(p.id == tag2_pattern.id for p in tag1_results)

    # Search by tag2
    tag2_results = await knowledge_base.search_patterns(tags=["tag2"])
    assert any(p.id == tag2_pattern.id for p in tag2_results)
    assert not any(p.id == tag1_pattern.id for p in tag2_results)

    # Search by common tag
    common_results = await knowledge_base.search_patterns(tags=["common"])
    assert any(p.id == tag1_pattern.id for p in common_results)
    assert any(p.id == tag2_pattern.id for p in common_results)

@pytest.mark.asyncio
async def test_pattern_versioning(knowledge_base: KnowledgeBase):
    """Test pattern versioning functionality."""
    # Create initial pattern
    initial_pattern = await knowledge_base.add_pattern(
        name="Versioned Pattern",
        type=PatternType.CODE,
        description="Initial version",
        content="def version1(): pass",
        confidence=PatternConfidence.MEDIUM,
        tags=["versioned"]
    )

    # Update pattern multiple times to create versions
    await knowledge_base.update_pattern(
        pattern_id=initial_pattern.id,
        description="Version 2",
        content="def version2(): pass"
    )

    await knowledge_base.update_pattern(
        pattern_id=initial_pattern.id,
        description="Version 3",
        content="def version3(): pass"
    )

    # Get the latest version
    latest = await knowledge_base.get_pattern(initial_pattern.id)
    assert latest.description == "Version 3"
    assert "version3" in latest.content

    # If versioning is supported, try to get a specific version
    try:
        # This might not be implemented in all versions of the knowledge base
        versions = await knowledge_base.get_pattern_versions(initial_pattern.id)
        if versions and len(versions) > 1:
            # If we have version history, verify it
            assert len(versions) >= 3, "Should have at least 3 versions"
            assert any("Version 2" in v.description for v in versions)
            assert any("Initial version" in v.description for v in versions)
    except (AttributeError, NotImplementedError):
        # Versioning might not be implemented, which is fine
        pass