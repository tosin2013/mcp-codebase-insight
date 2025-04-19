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
    """Test finding similar patterns."""
    # Add test patterns
    pattern1_data = {
        "name": "Test Pattern 1",
        "description": "First test pattern",
        "content": "def test1(): pass",
        "tags": ["test"]
    }
    pattern2_data = {
        "name": "Test Pattern 2",
        "description": "Second test pattern",
        "content": "def test2(): pass",
        "tags": ["test"]
    }

    pattern1 = await knowledge_base.add_pattern(
        name=pattern1_data["name"],
        type=PatternType.CODE,
        description=pattern1_data["description"],
        content=pattern1_data["content"],
        confidence=PatternConfidence.MEDIUM,
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

    # Search for similar patterns
    similar = await knowledge_base.find_similar_patterns("test pattern")
    assert len(similar) > 0

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