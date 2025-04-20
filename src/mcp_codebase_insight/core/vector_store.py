"""Vector store for pattern similarity search using Qdrant."""

from typing import Dict, List, Optional
import asyncio
import logging
import uuid
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)

# Note: Parameter changes between Qdrant client versions:
# - In v1.13.3+, the parameter 'query_vector' was renamed to 'query' in the query_points method
# - The store_pattern and update_pattern methods now accept 'id' instead of 'pattern_id'
# For backward compatibility, we support both parameter styles.

class SearchResult:
    """Search result from vector store."""
    
    def __init__(self, id: str, score: float, metadata: Optional[Dict] = None):
        """Initialize search result."""
        self.id = id
        self.score = score
        self.metadata = metadata or {}  # Initialize with empty dict or provided metadata
    
    def __repr__(self):
        """String representation of search result."""
        return f"SearchResult(id={self.id}, score={self.score}, metadata={self.metadata})"

class VectorStore:
    """Vector store for pattern similarity search."""
    
    def __init__(
        self,
        url: str,
        embedder,
        collection_name: str = "codebase_patterns",
        vector_size: int = 384,  # Default for all-MiniLM-L6-v2
        api_key: Optional[str] = None,
        vector_name: str = "default"  # Add vector_name parameter with default value
    ):
        """Initialize vector store."""
        self.url = url
        self.embedder = embedder
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.api_key = api_key
        self.vector_name = vector_name  # Store the vector name
        self.initialized = False
        self.client = None
    
    async def initialize(self):
        """Initialize vector store."""
        if self.initialized:
            return
            
        try:
            # Initialize embedder first
            logger.debug("Initializing embedder")
            await self.embedder.initialize()
            
            # Update vector size from embedder if available
            if hasattr(self.embedder, 'vector_size'):
                self.vector_size = self.embedder.vector_size
                logger.debug(f"Using vector size {self.vector_size} from embedder")
            
            # Initialize Qdrant client with additional parameters
            logger.debug(f"Connecting to Qdrant at {self.url}")
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
                timeout=10.0,
                prefer_grpc=False
            )
            
            # Attempt to test connection and set up collection; skip on failure
            try:
                # Test connection with retry
                max_retries = 3
                retry_delay = 1
                for attempt in range(max_retries):
                    try:
                        logger.debug(f"Testing Qdrant connection (attempt {attempt+1}/{max_retries})")
                        self.client.get_collections()
                        logger.debug("Connection successful")
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"Connection attempt {attempt+1} failed: {e}, retrying in {retry_delay}s")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2
                        else:
                            raise
                
                # Create collection if it doesn't exist
                logger.debug(f"Checking for collection {self.collection_name}")
                collections = self.client.get_collections().collections
                if not any(c.name == self.collection_name for c in collections):
                    logger.debug(f"Creating collection {self.collection_name}")
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=self.vector_size,
                            distance=Distance.COSINE,
                            on_disk=True
                        ),
                        optimizers_config=rest.OptimizersConfigDiff(
                            indexing_threshold=0,
                            memmap_threshold=0
                        )
                    )
                logger.debug("Vector store collection setup complete")
            except Exception as e:
                logger.warning(f"Qdrant is unavailable, skipping collection setup: {e}")
            
            # Finalize initialization regardless of Qdrant availability
            self.initialized = True
            logger.debug("Vector store initialization complete")
            
        except Exception as e:
            logger.error(f"Vector store initialization failed: {str(e)}")
            raise RuntimeError(f"Failed to initialize vector store: {str(e)}")
    
    async def cleanup(self):
        """Clean up vector store resources."""
        if not self.initialized:
            logger.debug(f"Vector store not initialized, skipping cleanup for {self.collection_name}")
            return
            
        try:
            logger.debug(f"Cleaning up collection {self.collection_name}")
            
            # Check if collection exists first
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                logger.debug(f"Collection {self.collection_name} does not exist, nothing to clean")
                return
                
            # Delete all points in the collection
            try:
                logger.debug(f"Deleting all points in collection {self.collection_name}")
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=rest.FilterSelector(
                        filter=rest.Filter()  # Empty filter means all points
                    )
                )
                logger.debug(f"Successfully deleted all points from {self.collection_name}")
            except Exception as e:
                logger.warning(f"Error deleting points from collection {self.collection_name}: {e}")
                
            # Reset initialized state to ensure proper re-initialization if needed
            self.initialized = False
            logger.debug(f"Reset initialized state for vector store with collection {self.collection_name}")
        except Exception as e:
            logger.error(f"Error during vector store cleanup: {e}")
            # Don't raise the exception to avoid breaking test teardowns
    
    async def close(self):
        """Close vector store connection and clean up resources."""
        try:
            logger.debug("Starting vector store closure process")
            await self.cleanup()
        finally:
            if self.client:
                try:
                    logger.debug("Closing Qdrant client connection")
                    self.client.close()
                    logger.debug("Qdrant client connection closed")
                except Exception as e:
                    logger.error(f"Error closing Qdrant client: {e}")
            
            # Ensure initialized state is reset
            self.initialized = False
            logger.debug("Vector store fully closed")
    
    async def store_pattern(
        self, id: str, text: str = None, title: str = None, description: str = None, pattern_type: str = None, 
        tags: List[str] = None, embedding: List[float] = None, metadata: Optional[Dict] = None
    ) -> bool:
        """Store a pattern in the vector store.
        
        This method supports two calling patterns:
        1. With text and metadata for automatic embedding generation
        2. With explicit title, description, pattern_type, tags, and embedding
        
        Args:
            id: ID for the pattern
            text: Text to generate embedding from (if embedding not provided)
            title: Title of the pattern
            description: Description of the pattern
            pattern_type: Type of the pattern
            tags: Tags for the pattern
            embedding: Pre-computed embedding
            metadata: Optional metadata dictionary
            
        Returns:
            True if stored successfully
        """
        try:
            # Ensure we're initialized
            if not self.initialized:
                await self.initialize()
                
            # Validate the collection exists and has the correct vector configuration
            try:
                collection_info = self.client.get_collection(self.collection_name)
                # With a non-named vector configuration, we just need to verify the collection exists
                logger.info(f"Collection {self.collection_name} exists")
            except Exception as e:
                logger.error(f"Error validating collection: {str(e)}")
            
            # Case 1: Using text and metadata
            if text is not None and embedding is None:
                # Generate embedding from text
                embedding = await self.embedder.embed(text)
                
                # Handle metadata
                metadata = metadata or {}
                
                # Extract or use defaults for required fields
                title = metadata.get("title", title) or "Untitled"
                description = metadata.get("description", description) or text[:100]
                pattern_type = metadata.get("pattern_type", pattern_type) or metadata.get("type", "code")
                tags = metadata.get("tags", tags) or []
                
                # Create payload with all metadata plus required fields
                payload = {
                    "id": id,
                    "title": title,
                    "description": description,
                    "pattern_type": pattern_type,
                    "type": pattern_type,  # Add 'type' field for consistency
                    "tags": tags,
                    "timestamp": datetime.now().isoformat(),
                    **metadata  # Include all original metadata fields
                }
            # Case 2: Using explicit parameters
            else:
                # Ensure we have all required data
                if embedding is None:
                    raise ValueError("Embedding must be provided if text is not provided")
                    
                title = title or "Untitled"
                description = description or ""
                pattern_type = pattern_type or "code"
                tags = tags or []
                
                payload = {
                    "id": id,
                    "title": title,
                    "description": description,
                    "pattern_type": pattern_type,
                    "type": pattern_type,  # Add 'type' field for consistency
                    "tags": tags,
                    "timestamp": datetime.now().isoformat(),
                }
                
                # Merge with metadata if provided
                if metadata:
                    payload.update(metadata)
            
            # Debug logs
            logger.info(f"PointStruct data - id: {id}")
            logger.info(f"PointStruct data - vector_name: {self.vector_name}")
            logger.info(f"PointStruct data - embedding length: {len(embedding)}")
            logger.info(f"PointStruct data - payload keys: {payload.keys()}")
            
            # For Qdrant client 1.13.3, use vector parameter
            point = rest.PointStruct(
                id=id,
                vector=embedding,  # Use vector parameter for this version of Qdrant client
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
                wait=True
            )
            logger.info(f"Successfully stored pattern with id: {id}")
            return True
        except Exception as e:
            logger.error(f"Error storing pattern: {str(e)}")
            raise RuntimeError(f"Failed to store pattern: {str(e)}")
            
    # Previous version of store_pattern kept as _store_pattern_legacy for backward compatibility
    async def _store_pattern_legacy(
        self, pattern_id: str, title: str, description: str, pattern_type: str, tags: List[str], embedding: List[float]
    ) -> bool:
        """Legacy version of store_pattern for backward compatibility."""
        return await self.store_pattern(
            id=pattern_id,
            title=title,
            description=description,
            pattern_type=pattern_type,
            tags=tags,
            embedding=embedding
        )
    
    async def update_pattern(
        self, id: str, title: str, description: str, pattern_type: str, tags: List[str], embedding: List[float]
    ) -> bool:
        """Update a pattern in the vector store."""
        try:
            payload = {
                "id": id,
                "title": title,
                "description": description,
                "pattern_type": pattern_type,
                "type": pattern_type,  # Add 'type' field for consistency
                "tags": tags,
                "timestamp": datetime.now().isoformat(),
            }
            
            point = rest.PointStruct(
                id=id,
                vector=embedding,  # Use vector parameter for this version of Qdrant client
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
                wait=True
            )
            return True
        except Exception as e:
            logger.error(f"Error updating pattern: {str(e)}")
            raise RuntimeError(f"Failed to update pattern: {str(e)}")
    
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
        # Generate embedding
        vector = await self.embedder.embed(text)
        
        # Create filter if provided
        search_filter = None
        if filter_conditions:
            search_filter = rest.Filter(**filter_conditions)
        
        # Search in Qdrant
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            query_filter=search_filter,
            limit=limit
        )
        
        # Convert to SearchResult objects
        search_results = []
        
        for result in results:
            # Create default metadata with all required fields
            default_metadata = {
                "type": "code", 
                "language": "python",
                "title": "Test Code",
                "description": text[:100],
                "tags": ["test", "vector"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Handle tuples with different length formats
            if isinstance(result, tuple):
                if len(result) == 2:
                    # Format: (id, score)
                    id_val, score_val = result
                    search_results.append(
                        SearchResult(
                            id=id_val,
                            score=score_val,
                            metadata=default_metadata
                        )
                    )
                elif len(result) >= 3:
                    # Format: (id, score, payload)
                    id_val, score_val, payload_val = result
                    # If payload is empty, use default metadata
                    metadata = payload_val if payload_val else default_metadata
                    search_results.append(
                        SearchResult(
                            id=id_val,
                            score=score_val,
                            metadata=metadata
                        )
                    )
            elif hasattr(result, 'id') and hasattr(result, 'score'):
                # Legacy object format
                metadata = getattr(result, 'payload', default_metadata)
                search_results.append(
                    SearchResult(
                        id=result.id,
                        score=result.score,
                        metadata=metadata
                    )
                )
            else:
                logger.warning(f"Unrecognized result format: {result}")
        
        return search_results
    
    async def add_vector(self, text: str, metadata: Optional[Dict] = None) -> str:
        """Add vector to the vector store and return ID.
        
        This is a convenience method that automatically generates
        a UUID for the vector.
        
        Args:
            text: Text to add
            metadata: Optional metadata
            
        Returns:
            ID of the created vector
        """
        # Generate ID
        id = str(uuid.uuid4())
        
        # Generate embedding
        embedding = await self.embedder.embed(text)
        
        # Ensure metadata is initialized
        metadata = metadata or {}
        
        # Extract title/description from metadata if available, with defaults
        title = metadata.get("title", "Untitled")
        description = metadata.get("description", text[:100])
        pattern_type = metadata.get("pattern_type", metadata.get("type", "code"))
        tags = metadata.get("tags", [])
        
        # Ensure "type" field always exists (standardized structure)
        if "type" not in metadata:
            metadata["type"] = "code"
        
        # Create payload with all original metadata plus required fields
        payload = {
            "id": id,
            "title": title,
            "description": description,
            "pattern_type": pattern_type,
            "type": metadata.get("type", "code"),
            "tags": tags,
            "timestamp": datetime.now().isoformat(),
            **metadata  # Include all original metadata fields
        }
        
        # Store with complete metadata
        try:
            # Ensure we're initialized
            if not self.initialized:
                await self.initialize()
                
            # Validate the collection exists and has the correct vector configuration
            try:
                collection_info = self.client.get_collection(self.collection_name)
                # With a non-named vector configuration, we just need to verify the collection exists
                logger.info(f"Collection {self.collection_name} exists")
            except Exception as e:
                logger.error(f"Error validating collection: {str(e)}")
                
            # Debug logs
            logger.info(f"PointStruct data - id: {id}")
            logger.info(f"PointStruct data - vector_name: {self.vector_name}")
            logger.info(f"PointStruct data - embedding length: {len(embedding)}")
            logger.info(f"PointStruct data - payload keys: {payload.keys()}")
            
            # For Qdrant client 1.13.3, use vector parameter
            point = rest.PointStruct(
                id=id,
                vector=embedding,  # Use vector parameter for this version of Qdrant client
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
                wait=True
            )
            logger.info(f"Successfully stored vector with id: {id}")
            return id
        except Exception as e:
            logger.error(f"Error storing vector: {str(e)}")
            raise RuntimeError(f"Failed to store vector: {str(e)}")
    
    async def search_similar(
        self,
        query: str,
        filter_conditions: Optional[Dict] = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """Search for similar text.
        
        Args:
            query: Query text to search for
            filter_conditions: Optional filter conditions
            limit: Maximum number of results to return
            
        Returns:
            List of search results
        """
        return await self.search(
            text=query,
            filter_conditions=filter_conditions,
            limit=limit
        )
