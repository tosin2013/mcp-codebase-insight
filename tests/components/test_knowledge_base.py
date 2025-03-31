
import sys
import os

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from pathlib import Path
from typing import AsyncGenerator
from src.mcp_codebase_insight.core.knowledge import KnowledgeBase, PatternType, PatternConfidence
from src.mcp_codebase_insight.core.config import ServerConfig
from src.mcp_codebase_insight.core.vector_store import VectorStore

@pytest.fixture
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