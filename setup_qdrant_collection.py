from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

def setup_collection():
    # Connect to Qdrant
    client = QdrantClient(
        url='https://e67ee53a-6e03-4526-9e41-3fde622323a9.us-east4-0.gcp.cloud.qdrant.io:6333',
        api_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzQ1MTAyNzQ3fQ.3gvK8M7dJxZkSpyzpJtTGVUhjyjgbYEhEvl2aG7JodM'
    )
    
    collection_name = "mcp-codebase-insight"
    
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        # If collection exists, recreate it
        if exists:
            print(f"\nRemoving existing collection '{collection_name}'")
            client.delete_collection(collection_name=collection_name)
        
        # Create a new collection with named vector configurations
        print(f"\nCreating collection '{collection_name}' with named vectors")
        
        # Create named vectors configuration
        vectors_config = {
            # For the default MCP server embedding model (all-MiniLM-L6-v2)
            "fast-all-minilm-l6-v2": VectorParams(
                size=384,  # all-MiniLM-L6-v2 produces 384-dimensional vectors
                distance=Distance.COSINE
            )
        }
        
        client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config
        )
        
        # Verify the collection was created properly
        collection_info = client.get_collection(collection_name=collection_name)
        print(f"\nCollection '{collection_name}' created successfully")
        print(f"Vector configuration: {collection_info.config.params.vectors}")
        
        print("\nCollection is ready for the MCP server")
        
    except Exception as e:
        print(f"\nError setting up collection: {e}")

if __name__ == '__main__':
    setup_collection() 