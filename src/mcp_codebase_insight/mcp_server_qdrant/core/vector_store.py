from typing import Dict, List, Optional, Any
import asyncio
import time
import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams

from .embeddings import EmbeddingProvider
from .metrics import MetricsCollector
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SearchResult:
    """Result from vector search."""
    id: str
    score: float
    payload: Dict[str, Any]

class VectorStore:
    """Vector store using Qdrant."""

    def __init__(
        self,
        client: QdrantClient,
        embedder: EmbeddingProvider,
        collection_name: str,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """Initialize vector store."""
        self.client = client
        self.embedder = embedder
        self.collection_name = collection_name
        self.metrics_collector = metrics_collector
        self.embedding_dim = embedder.get_dimension()

    async def initialize(self) -> None:
        """Initialize vector store."""
        # Check if collection exists
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
        
        # Create index
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="type",
            field_schema=rest.PayloadSchemaType.KEYWORD
        )

    async def store(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store text with metadata."""
        start_time = time.time()
        
        try:
            # Generate embedding
            embedding = await self.embedder.embed_text(text)
            
            # Generate UUID for point ID
            point_id = str(uuid.uuid4())
            
            # Store in Qdrant
            points = rest.Batch(
                ids=[point_id],
                vectors=[embedding],
                payloads=[metadata or {}]
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            if self.metrics_collector:
                duration = time.time() - start_time
                await self.metrics_collector.record_vector_query(
                    operation="store",
                    duration=duration
                )
            
            return point_id
            
        except Exception as e:
            logger.error(f"Error storing vector: {e}")
            raise

    async def store_batch(
        self,
        texts: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Store multiple texts with metadata."""
        start_time = time.time()
        
        try:
            # Generate embeddings
            embeddings = await self.embedder.embed_texts(texts)
            
            # Prepare points with UUIDs
            if metadata is None:
                metadata = [{} for _ in texts]
            
            point_ids = [str(uuid.uuid4()) for _ in texts]
            points = rest.Batch(
                ids=point_ids,
                vectors=embeddings,
                payloads=metadata
            )
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            if self.metrics_collector:
                duration = time.time() - start_time
                await self.metrics_collector.record_vector_query(
                    operation="store_batch",
                    duration=duration
                )
            
            return point_ids
            
        except Exception as e:
            logger.error(f"Error storing vectors: {e}")
            raise

    async def search(
        self,
        text: str,
        filter_params: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """Search for similar texts."""
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_vector = await self.embedder.embed_text(text)
            
            # Convert filter params to Qdrant format
            filter_conditions = None
            if filter_params:
                filter_conditions = self._build_filter(filter_params)
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=filter_conditions,
                limit=limit
            )
            
            if self.metrics_collector:
                duration = time.time() - start_time
                await self.metrics_collector.record_vector_query(
                    operation="search",
                    duration=duration
                )
            
            # Convert results
            return [
                SearchResult(
                    id=str(r.id),
                    score=r.score,
                    payload=r.payload
                )
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise

    async def update(
        self,
        id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update stored text and metadata."""
        start_time = time.time()
        
        try:
            # Generate new embedding
            embedding = await self.embedder.embed_text(text)
            
            # Update in Qdrant
            self.client.update(
                collection_name=self.collection_name,
                points=rest.Batch(
                    ids=[id],
                    vectors=[embedding],
                    payloads=[metadata or {}]
                )
            )
            
            if self.metrics_collector:
                duration = time.time() - start_time
                await self.metrics_collector.record_vector_query(
                    operation="update",
                    duration=duration
                )
            
        except Exception as e:
            logger.error(f"Error updating vector: {e}")
            raise

    async def delete(self, id: str) -> None:
        """Delete stored text."""
        start_time = time.time()
        
        try:
            # Delete from Qdrant
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest.PointIdsList(
                    points=[id]
                )
            )
            
            if self.metrics_collector:
                duration = time.time() - start_time
                await self.metrics_collector.record_vector_query(
                    operation="delete",
                    duration=duration
                )
            
        except Exception as e:
            logger.error(f"Error deleting vector: {e}")
            raise

    async def get(self, id: str) -> Optional[SearchResult]:
        """Get stored text by ID."""
        start_time = time.time()
        
        try:
            # Get from Qdrant
            results = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[id]
            )
            
            if self.metrics_collector:
                duration = time.time() - start_time
                await self.metrics_collector.record_vector_query(
                    operation="get",
                    duration=duration
                )
            
            if not results:
                return None
            
            result = results[0]
            return SearchResult(
                id=str(result.id),
                score=1.0,  # Exact match
                payload=result.payload
            )
            
        except Exception as e:
            logger.error(f"Error getting vector: {e}")
            raise

    async def list(
        self,
        filter_params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[SearchResult]:
        """List stored texts with optional filtering."""
        start_time = time.time()
        
        try:
            # Convert filter params to Qdrant format
            filter_conditions = None
            if filter_params:
                filter_conditions = self._build_filter(filter_params)
            
            # Get from Qdrant
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_conditions,
                limit=limit,
                offset=offset
            )[0]  # scroll returns (points, next_page_offset)
            
            if self.metrics_collector:
                duration = time.time() - start_time
                await self.metrics_collector.record_vector_query(
                    operation="list",
                    duration=duration
                )
            
            # Convert results
            return [
                SearchResult(
                    id=str(r.id),
                    score=1.0,  # Not a similarity search
                    payload=r.payload
                )
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Error listing vectors: {e}")
            raise

    def _build_filter(self, params: Dict[str, Any]) -> rest.Filter:
        """Build Qdrant filter from parameters."""
        conditions = []
        
        if "must" in params:
            for condition in params["must"]:
                if "match" in condition:
                    conditions.append(
                        rest.FieldCondition(
                            key=condition["key"],
                            match=rest.MatchValue(**condition["match"])
                        )
                    )
                elif "range" in condition:
                    conditions.append(
                        rest.FieldCondition(
                            key=condition["key"],
                            range=rest.Range(**condition["range"])
                        )
                    )
        
        if "must_not" in params:
            for condition in params["must_not"]:
                if "match" in condition:
                    conditions.append(
                        rest.FieldCondition(
                            key=condition["key"],
                            match=rest.MatchValue(**condition["match"]),
                            is_negated=True
                        )
                    )
                elif "range" in condition:
                    conditions.append(
                        rest.FieldCondition(
                            key=condition["key"],
                            range=rest.Range(**condition["range"]),
                            is_negated=True
                        )
                    )
        
        return rest.Filter(
            must=conditions
        )

    async def close(self) -> None:
        """Close vector store connection."""
        self.client.close()
