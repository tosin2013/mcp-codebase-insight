"""Vector store for semantic search using Qdrant."""

from typing import List, Optional, Dict, Any
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models

from mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding
from mcp_codebase_insight.core.errors import VectorStoreError
from mcp_codebase_insight.utils.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    """Vector store for semantic search."""

    def __init__(
        self,
        client: QdrantClient,
        embedder: SentenceTransformerEmbedding,
        collection_name: str
    ):
        """Initialize vector store."""
        self.client = client
        self.embedder = embedder
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure collection exists with correct settings."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                logger.info(f"Creating collection {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.embedder.get_dimension(),
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            raise VectorStoreError(f"Failed to ensure collection: {e}")

    def add_points(
        self,
        texts: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add points to vector store."""
        try:
            embeddings = self.embedder.embed(texts)
            
            if metadata is None:
                metadata = [{} for _ in texts]
            
            if ids is None:
                from uuid import uuid4
                ids = [str(uuid4()) for _ in texts]

            points = [
                models.PointStruct(
                    id=id_,
                    vector=embedding.tolist(),
                    payload=meta
                )
                for id_, embedding, meta in zip(ids, embeddings, metadata)
            ]

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            return ids
        except Exception as e:
            raise VectorStoreError(f"Failed to add points: {e}")

    def search(
        self,
        query: str,
        limit: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar points."""
        try:
            embedding = self.embedder.embed(query)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding[0].tolist(),
                limit=limit,
                query_filter=filter
            )

            return [
                {
                    "id": str(r.id),
                    "score": r.score,
                    "payload": r.payload
                }
                for r in results
            ]
        except Exception as e:
            raise VectorStoreError(f"Failed to search: {e}")

    def delete_points(self, ids: List[str]):
        """Delete points from vector store."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=ids
                )
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to delete points: {e}")

    def clear_collection(self):
        """Clear all points from collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection()
        except Exception as e:
            raise VectorStoreError(f"Failed to clear collection: {e}")
