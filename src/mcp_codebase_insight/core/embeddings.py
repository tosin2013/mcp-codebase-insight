"""Vector embeddings for semantic search."""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from mcp_codebase_insight.core.errors import VectorStoreError

class SentenceTransformerEmbedding:
    """Sentence transformer based embeddings."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the embedding model."""
        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise VectorStoreError(f"Failed to load embedding model: {e}")

    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text."""
        try:
            if isinstance(text, str):
                text = [text]
            embeddings = self.model.encode(text, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            raise VectorStoreError(f"Failed to generate embeddings: {e}")

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension
