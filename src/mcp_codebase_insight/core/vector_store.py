"""Vector store for pattern similarity search using Qdrant."""

from typing import Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams

class SearchResult:
    """Search result from vector store."""
    
    def __init__(self, id: str, score: float):
        """Initialize search result."""
        self.id = id
        self.score = score

class VectorStore:
    """Vector store for pattern similarity search."""
    
    def __init__(
        self,
        url: str,
        embedder,
        collection_name: str = "codebase_patterns",
        vector_size: int = 384  # Default for all-MiniLM-L6-v2
    ):
        """Initialize vector store."""
        self.client = QdrantClient(url=url)
        self.embedder = embedder
        self.collection_name = collection_name
        self.vector_size = vector_size
    
    async def initialize(self):
        """Initialize vector store."""
        try:
            # Create collection if it doesn't exist
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
            
            # Ensure collection is ready
            self.client.get_collection(self.collection_name)
        except Exception as e:
            # If there's an error, try to recreate the collection
            try:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
            except Exception as inner_e:
                raise RuntimeError(f"Failed to initialize vector store: {str(inner_e)}") from e
    
    async def cleanup(self):
        """Clean up vector store resources."""
        # Nothing to clean up for now
        pass
    
    async def store_pattern(
        self,
        id: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Store pattern in vector store."""
        # Generate embedding
        vector = await self.embedder.embed(text)
        
        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                rest.PointStruct(
                    id=id,
                    vector=vector,
                    payload=metadata or {}
                )
            ]
        )
    
    async def update_pattern(
        self,
        id: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Update pattern in vector store."""
        # Generate new embedding
        vector = await self.embedder.embed(text)
        
        # Update in Qdrant
        self.client.update(
            collection_name=self.collection_name,
            points=[
                rest.PointStruct(
                    id=id,
                    vector=vector,
                    payload=metadata or {}
                )
            ]
        )
    
    async def delete_pattern(self, id: str) -> None:
        """Delete pattern from vector store."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=rest.PointIdsList(
                points=[id]
            )
        )
    
    async def search(
        self,
        text: str,
        filter_conditions: Optional[Dict] = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """Search for similar patterns."""
        # Generate query embedding
        query_vector = await self.embedder.embed(text)
        
        # Build filter if conditions provided
        search_filter = None
        if filter_conditions:
            filter_clauses = []
            for field, value in filter_conditions.items():
                if isinstance(value, dict) and "$all" in value:
                    # Handle array contains all filter
                    filter_clauses.append(
                        rest.HasIdFilter(
                            has_id=[str(v) for v in value["$all"]]
                        )
                    )
                else:
                    # Handle simple equality filter
                    filter_clauses.append(
                        rest.FieldCondition(
                            key=field,
                            match=rest.MatchValue(value=value)
                        )
                    )
            search_filter = rest.Filter(
                must=filter_clauses
            )
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=limit
        )
        
        # Convert to SearchResult objects
        return [
            SearchResult(
                id=str(hit.id),
                score=hit.score
            )
            for hit in results
        ]
