"""Text embedding using sentence-transformers."""

from typing import List, Union

from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbedding:
    """Text embedding using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedding model."""
        try:
            self.model = SentenceTransformer(model_name)
            self.vector_size = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model {model_name}: {str(e)}")
    
    async def embed(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for text."""
        try:
            # Convert single string to list for consistent handling
            texts = [text] if isinstance(text, str) else text
            
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                convert_to_tensor=False,  # Return numpy array
                normalize_embeddings=True  # L2 normalize embeddings
            )
            
            # Convert numpy arrays to lists for JSON serialization
            if isinstance(text, str):
                return embeddings[0].tolist()
            return [embedding.tolist() for embedding in embeddings]
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")
    
    async def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await self.embed(batch)
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    async def embed_with_cache(
        self,
        text: str,
        cache_manager = None
    ) -> List[float]:
        """Generate embeddings with caching."""
        if not cache_manager:
            return await self.embed(text)
            
        # Try to get from cache
        cache_key = f"embedding:{hash(text)}"
        cached = cache_manager.get_from_memory(cache_key)
        if cached:
            return cached
            
        # Generate new embedding
        embedding = await self.embed(text)
        
        # Cache the result
        cache_manager.put_in_memory(cache_key, embedding)
        return embedding
    
    def get_vector_size(self) -> int:
        """Get the size of embedding vectors."""
        return self.vector_size
