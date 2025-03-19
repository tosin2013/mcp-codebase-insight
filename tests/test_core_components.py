"""Tests for core components."""

import pytest
from typing import List

from src.mcp_server_qdrant.core.vector_store import VectorStore, SearchResult
from src.mcp_server_qdrant.core.knowledge import KnowledgeBase, PatternType
from src.mcp_server_qdrant.core.embeddings import EmbeddingProvider

@pytest.mark.asyncio
async def test_vector_store_basic_operations(vector_store: VectorStore):
    """Test basic vector store operations."""
    # Test storing text
    text = "This is a test document"
    metadata = {"type": "test", "source": "unit_test"}
    
    doc_id = await vector_store.store(text, metadata)
    assert doc_id is not None
    
    # Test searching
    results = await vector_store.search(text, limit=1)
    assert len(results) == 1
    assert results[0].score > 0.9  # Should be very similar to original
    assert results[0].payload["type"] == "test"
    
    # Test getting by ID
    result = await vector_store.get(doc_id)
    assert result is not None
    assert result.payload["source"] == "unit_test"
    
    # Test updating
    new_text = "Updated test document"
    await vector_store.update(doc_id, new_text, {"type": "test", "updated": True})
    
    result = await vector_store.get(doc_id)
    assert result is not None
    assert result.payload["updated"] is True
    
    # Test deleting
    await vector_store.delete(doc_id)
    result = await vector_store.get(doc_id)
    assert result is None

@pytest.mark.asyncio
async def test_vector_store_batch_operations(vector_store: VectorStore):
    """Test batch operations in vector store."""
    texts = [
        "First test document",
        "Second test document",
        "Third test document"
    ]
    metadata = [
        {"index": 0},
        {"index": 1},
        {"index": 2}
    ]
    
    # Test batch store
    ids = await vector_store.store_batch(texts, metadata)
    assert len(ids) == 3
    
    # Test listing
    results = await vector_store.list(limit=10)
    assert len(results) == 3
    
    # Test filtering
    results = await vector_store.list(
        filter_params={
            "must": [
                {
                    "key": "index",
                    "match": {"value": 1}
                }
            ]
        }
    )
    assert len(results) == 1
    assert results[0].payload["index"] == 1

@pytest.mark.asyncio
async def test_knowledge_base_pattern_operations(
    knowledge_base: KnowledgeBase
):
    """Test knowledge base pattern operations."""
    # Test storing pattern
    pattern = await knowledge_base.store_pattern(
        type=PatternType.CODE,
        name="Test Pattern",
        description="A test pattern",
        content="Test pattern content",
        examples=["Example 1", "Example 2"],
        context={"language": "python"},
        tags={"test", "pattern"}
    )
    assert pattern.id is not None
    
    # Test getting pattern
    result = await knowledge_base.get_pattern(pattern.id)
    assert result is not None
    assert result.name == "Test Pattern"
    assert result.type == PatternType.CODE
    
    # Test searching patterns
    results = await knowledge_base.find_similar_patterns(
        text="test pattern python",
        type=PatternType.CODE
    )
    assert len(results) > 0
    assert results[0].name == "Test Pattern"
    
    # Test listing patterns
    patterns = await knowledge_base.list_patterns(
        type=PatternType.CODE,
        tags={"test"}
    )
    assert len(patterns) == 1
    assert patterns[0].name == "Test Pattern"
    
    # Test updating pattern
    await knowledge_base.update_pattern(
        pattern,
        {"description": "Updated description"},
        success=True
    )
    
    result = await knowledge_base.get_pattern(pattern.id)
    assert result is not None
    assert result.description == "Updated description"
    assert result.usage_count == 1
    assert result.success_rate == 1.0

@pytest.mark.asyncio
async def test_embedding_provider_operations(
    embedding_provider: EmbeddingProvider
):
    """Test embedding provider operations."""
    # Test single text embedding
    text = "This is a test document"
    embedding = await embedding_provider.embed_text(text)
    assert len(embedding) == embedding_provider.embedding_dim
    
    # Test batch text embedding
    texts = [
        "First test document",
        "Second test document",
        "Third test document"
    ]
    embeddings = await embedding_provider.embed_texts(texts)
    assert len(embeddings) == 3
    assert all(len(emb) == embedding_provider.embedding_dim for emb in embeddings)
    
    # Test similarity computation
    similarity = await embedding_provider.compute_similarity(
        embeddings[0],
        embeddings[1]
    )
    assert 0 <= similarity <= 1
    
    # Test nearest neighbors
    neighbors = await embedding_provider.find_nearest_neighbors(
        embeddings[0],
        embeddings[1:],
        k=2
    )
    assert len(neighbors) == 2
    assert all("score" in n and "index" in n for n in neighbors)
    
    # Test dimensionality reduction
    reduced = await embedding_provider.reduce_dimensions(
        embeddings,
        n_components=2
    )
    assert len(reduced) == 3
    assert all(len(vec) == 2 for vec in reduced)
    
    # Test clustering
    clusters = await embedding_provider.cluster_embeddings(
        embeddings,
        n_clusters=2
    )
    assert len(clusters) == 3
    assert all(isinstance(c, int) for c in clusters)

@pytest.mark.asyncio
async def test_error_handling(vector_store: VectorStore):
    """Test error handling in core components."""
    # Test invalid ID
    with pytest.raises(Exception):
        await vector_store.get("nonexistent_id")
    
    # Test invalid filter
    with pytest.raises(Exception):
        await vector_store.list(filter_params={"invalid": "filter"})
    
    # Test invalid update
    with pytest.raises(Exception):
        await vector_store.update("nonexistent_id", "text", {})
    
    # Test invalid delete
    with pytest.raises(Exception):
        await vector_store.delete("nonexistent_id")
