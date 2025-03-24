"""Text embedding using sentence-transformers."""

from typing import List, Union
import asyncio
import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class SentenceTransformerEmbedding:
    """Text embedding using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedding model."""
        self.model_name = model_name
        self.model = None
        self.vector_size = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the embedding model."""
        if self.initialized:
            return

        max_retries = 3
        retry_delay = 2.0

        for attempt in range(max_retries):
            try:
                # Define the model loading function
                def load_model():
                    logger.debug(f"Loading model {self.model_name}")
                    model = SentenceTransformer(self.model_name)
                    vector_size = model.get_sentence_embedding_dimension()
                    return model, vector_size

                # Load the model with a timeout
                logger.debug(f"Starting model loading attempt {attempt + 1}/{max_retries}")
                model, vector_size = await asyncio.to_thread(load_model)
                
                self.model = model
                self.vector_size = vector_size
                self.initialized = True
                logger.debug(f"Model loaded successfully with vector size {self.vector_size}")
                return
                
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    logger.warning(f"Timeout loading model on attempt {attempt + 1}, retrying in {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to load model after {max_retries} attempts")
                    raise RuntimeError(f"Failed to load embedding model {self.model_name}: Timeout after {max_retries} attempts")
            except Exception as e:
                logger.error(f"Failed to load embedding model {self.model_name}: {str(e)}")
                raise RuntimeError(f"Failed to load embedding model {self.model_name}: {str(e)}")
    
    async def embed(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for text."""
        if not self.initialized:
            await self.initialize()
        
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
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")
    
    async def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Generate embeddings in batches
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                embeddings = self.model.encode(
                    batch,
                    convert_to_tensor=False,
                    normalize_embeddings=True,
                    batch_size=batch_size
                )
                all_embeddings.extend(embeddings.tolist())
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")
    
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
