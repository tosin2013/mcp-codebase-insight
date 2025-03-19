from abc import ABC, abstractmethod
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        pass

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass

class SentenceTransformerEmbedding(EmbeddingProvider):
    """Sentence transformer based embedding provider."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize with model name."""
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        embedding = self.model.encode(text)
        return embedding.tolist()

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
