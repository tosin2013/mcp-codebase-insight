import pytest
import asyncio
from mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding

@pytest.mark.asyncio
async def test_embedder_initialization():
    """Test that embedder initializes correctly."""
    embedder = SentenceTransformerEmbedding()
    try:
        await asyncio.wait_for(embedder.initialize(), timeout=60.0)
        assert embedder.model is not None
        assert embedder.vector_size == 384  # Default size for all-MiniLM-L6-v2
    except asyncio.TimeoutError:
        pytest.fail("Embedder initialization timed out")
    except Exception as e:
        pytest.fail(f"Embedder initialization failed: {str(e)}")

@pytest.mark.asyncio
async def test_embedder_embedding():
    """Test that embedder can generate embeddings."""
    embedder = SentenceTransformerEmbedding()
    await embedder.initialize()
    
    # Test single text embedding
    text = "Test text"
    embedding = await embedder.embed(text)
    assert len(embedding) == embedder.vector_size
    
    # Test batch embedding
    texts = ["Test text 1", "Test text 2"]
    embeddings = await embedder.embed_batch(texts)
    assert len(embeddings) == 2
    assert all(len(emb) == embedder.vector_size for emb in embeddings) 