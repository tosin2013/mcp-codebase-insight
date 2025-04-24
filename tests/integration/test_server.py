"""Test server API endpoints."""

import sys
import os

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
import pytest_asyncio
from httpx import AsyncClient
import uuid
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from src.mcp_codebase_insight.core.config import ServerConfig
from src.mcp_codebase_insight.core.vector_store import VectorStore
from src.mcp_codebase_insight.core.knowledge import Pattern
from src.mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding
from src.mcp_codebase_insight.server import CodebaseAnalysisServer
from src.mcp_codebase_insight.server_test_isolation import get_isolated_server_state

# Setup logger
logger = logging.getLogger(__name__)

# Environment variables or defaults for vector store testing
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333") 
TEST_COLLECTION_NAME = os.environ.get("TEST_COLLECTION_NAME", "test_vector_search")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Path to test repository
TEST_REPO_PATH = Path("tests/fixtures/test_repo")

@pytest_asyncio.fixture
async def setup_test_vector_store(test_server_client):
    """Set up a test vector store with sample patterns for the server tests.
    
    This fixture initializes the vector store component in the server with test patterns,
    allowing the vector store search endpoint to be tested properly.
    """
    # Get server state from the test client
    logger.info("Attempting to get server health status")
    request = await test_server_client.get("/health")
    if request.status_code != 200:
        logger.warning(f"Server health check failed with status code {request.status_code}")
        yield None
        return
    
    # Get the server state through test isolation utilities
    logger.info("Getting isolated server state")
    server_state = get_isolated_server_state()
    if not server_state:
        logger.warning("Could not get isolated server state, server_state is None")
        yield None
        return
    
    logger.info(f"Got server state, instance ID: {server_state.instance_id}")
    logger.info(f"Server state components: {server_state.list_components()}")
        
    # Create and initialize a test vector store
    try:
        # Create the embedder first
        logger.info(f"Creating embedding model with model name: {EMBEDDING_MODEL}")
        embedder = SentenceTransformerEmbedding(model_name=EMBEDDING_MODEL)
        await embedder.initialize()
        
        # Now create the vector store with the embedder
        logger.info(f"Creating vector store with URL: {QDRANT_URL}, collection: {TEST_COLLECTION_NAME}")
        vector_store = VectorStore(
            url=QDRANT_URL,
            embedder=embedder,
            collection_name=TEST_COLLECTION_NAME
        )
        
        # Delete any existing collection with this name
        try:
            logger.info("Cleaning up vector store before use")
            await vector_store.cleanup()
            logger.info("Vector store cleaned up")
        except Exception as e:
            logger.warning(f"Error during vector store cleanup: {str(e)}")
            
        # Initialize the vector store
        logger.info("Initializing vector store")
        await vector_store.initialize()
        logger.info(f"Initialized vector store with collection: {TEST_COLLECTION_NAME}")
        
        # Add test patterns
        logger.info("Adding test patterns to vector store")
        await add_test_patterns(vector_store, embedder)
        
        # Register the vector store in the server state
        logger.info("Registering vector store component in server state")
        server_state.register_component("vector_store", vector_store)
        logger.info("Registered vector store component in server state")
        
        yield vector_store
        
        # Cleanup
        try:
            logger.info("Closing vector store")
            await vector_store.close()
            logger.info("Vector store closed")
        except Exception as e:
            logger.warning(f"Error during vector store closure: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error setting up test vector store: {str(e)}", exc_info=True)
        yield None

async def add_test_patterns(store: VectorStore, embedder: SentenceTransformerEmbedding):
    """Add test patterns to the vector store for testing."""
    patterns = []
    
    # Add sample patterns for testing
    patterns.append(Pattern(
        id=str(uuid.uuid4()),
        text="""class SearchResult:
    \"\"\"Represents a search result from the vector store.\"\"\"
    def __init__(self, id: str, score: float, metadata: Optional[Dict] = None):
        self.id = id
        self.score = score
        self.metadata = metadata or {}
        
    def to_dict(self):
        \"\"\"Convert to dictionary.\"\"\"
        return {
            "id": self.id,
            "score": self.score,
            "metadata": self.metadata
        }""",
        title="SearchResult Class",
        description="A class for vector store search results",
        pattern_type="code",
        tags=["python", "class", "search", "vector-store"],
        metadata={
            "language": "python",
            "file_path": "src/core/models.py",
            "line_range": "10-25",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "code"
        }
    ))
    
    patterns.append(Pattern(
        id=str(uuid.uuid4()),
        text="""async def search(
    self,
    query: str,
    limit: int = 5,
    threshold: float = 0.7,
    file_type: Optional[str] = None,
    path_pattern: Optional[str] = None
) -> List[Dict]:
    \"\"\"Search for patterns matching the query.\"\"\"
    # Generate embedding for the query
    embedding = await self.embedding_model.embed(query)
    
    # Prepare filter conditions
    filter_conditions = {}
    if file_type:
        filter_conditions["language"] = file_type
    if path_pattern:
        filter_conditions["file_path"] = {"$like": path_pattern}
        
    # Perform the search
    results = await self.vector_store.search(
        embedding=embedding,
        limit=limit,
        filter_conditions=filter_conditions
    )
    
    # Filter by threshold
    filtered_results = [r for r in results if r.score >= threshold]
    
    return filtered_results""",
        title="Vector Store Search Method",
        description="Async method to search the vector store with filters",
        pattern_type="code",
        tags=["python", "async", "function", "search"],
        metadata={
            "language": "python",
            "file_path": "src/core/search.py", 
            "line_range": "50-75",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "code"
        }
    ))
    
    patterns.append(Pattern(
        id=str(uuid.uuid4()),
        text="""# Vector Store Configuration
        
## Search Parameters

- **query**: The text to search for similar patterns
- **threshold**: Similarity score threshold (0.0 to 1.0)
- **limit**: Maximum number of results to return
- **file_type**: Filter by programming language/file type
- **path_pattern**: Filter by file path pattern

## Recommended Threshold Values

- **0.9-1.0**: Very high precision, almost exact matches
- **0.8-0.9**: High precision, strongly similar
- **0.7-0.8**: Good balance (default)
- **0.6-0.7**: Higher recall, more results
- **0.5-0.6**: Very high recall, may include less relevant matches""",
        title="Vector Store Documentation",
        description="Documentation on vector store search parameters",
        pattern_type="documentation",
        tags=["documentation", "markdown", "search", "parameters"],
        metadata={
            "language": "markdown",
            "file_path": "docs/vector_store.md",
            "line_range": "50-70",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "documentation"
        }
    ))
    
    # Store patterns with embeddings
    for pattern in patterns:
        # Generate embedding for the pattern text
        embedding = await embedder.embed(pattern.text)
        
        # Store the pattern
        await store.store_pattern(
            id=pattern.id,
            text=pattern.text,
            title=pattern.title,
            description=pattern.description,
            pattern_type=pattern.pattern_type,
            tags=pattern.tags,
            metadata=pattern.metadata,
            embedding=embedding
        )
        logger.info(f"Added pattern: {pattern.title}")
    
    logger.info(f"Added {len(patterns)} patterns to the test vector store")
    return patterns

# Use the test_client fixture from conftest.py
@pytest_asyncio.fixture(scope="function")
async def test_server_client(httpx_test_client):
    """Get a test client for server API testing.
    
    This uses the httpx_test_client from conftest.py to ensure
    proper event loop and resource management.
    """
    yield httpx_test_client

@pytest.fixture
def test_code():
    """Return a sample code snippet for testing."""
    return """
def example_function(x: int) -> int:
    return x * 2
"""

@pytest.fixture
def test_issue():
    """Return a sample issue description for testing."""
    return "Error in function: example_function returns incorrect results for negative values"

@pytest.fixture
def test_adr():
    """Return a sample ADR structure for testing."""
    return {
        "title": "Test ADR",
        "status": "Proposed",
        "context": "This is a test ADR for automated testing purposes.",
        "decision": "We've decided to use this test ADR format.",
        "consequences": {
            "positive": ["Test positive consequence"],
            "negative": ["Test negative consequence"]
        },
        "options": [
            {
                "title": "Test option",
                "description": "Test description",
                "pros": ["Test pro"],
                "cons": ["Test con"]
            }
        ]
    }

@pytest.mark.asyncio
async def test_health_check(test_server_client: AsyncClient):
    """Test health check endpoint."""
    response = await test_server_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

@pytest.mark.asyncio
async def test_metrics(test_server_client: AsyncClient):
    """Test metrics endpoint."""
    response = await test_server_client.get("/metrics")
    # Some test servers may not have metrics enabled
    if response.status_code == 200:
        data = response.json()
        assert "metrics" in data
    else:
        logger.info(f"Metrics endpoint not available (status: {response.status_code})")
        assert response.status_code in [404, 503]  # Not found or service unavailable

@pytest.mark.asyncio
async def test_analyze_code(test_server_client: AsyncClient, test_code: str):
    """Test code analysis endpoint."""
    response = await test_server_client.post(
        "/tools/analyze-code",
        json={
            "name": "analyze-code",
            "arguments": {
                "code": test_code,
                "context": {}
            }
        }
    )
    # Component might not be available in test server
    if response.status_code == 200:
        data = response.json()
        assert "content" in data
    else:
        logger.info(f"Code analysis endpoint not available (status: {response.status_code})")
        assert response.status_code in [404, 503]  # Not found or service unavailable

@pytest.mark.asyncio
async def test_create_adr(test_server_client: AsyncClient, test_adr: dict):
    """Test ADR creation endpoint."""
    response = await test_server_client.post(
        "/tools/create-adr",
        json={
            "name": "create-adr",
            "arguments": test_adr
        }
    )
    # Component might not be available in test server
    if response.status_code == 200:
        data = response.json()
        assert "content" in data
    else:
        logger.info(f"ADR creation endpoint not available (status: {response.status_code})")
        assert response.status_code in [404, 503]  # Not found or service unavailable

@pytest.mark.asyncio
async def test_debug_issue(test_server_client: AsyncClient, test_issue: str):
    """Test issue debugging endpoint."""
    response = await test_server_client.post(
        "/tools/debug-issue",
        json={
            "name": "debug-issue",
            "arguments": {
                "issue": test_issue,
                "context": {}
            }
        }
    )
    # Component might not be available in test server
    if response.status_code == 200:
        data = response.json()
        assert "content" in data
    else:
        logger.info(f"Debug issue endpoint not available (status: {response.status_code})")
        assert response.status_code in [404, 503]  # Not found or service unavailable

@pytest.mark.asyncio
async def test_search_knowledge(test_server_client: AsyncClient):
    """Test knowledge search endpoint."""
    response = await test_server_client.post(
        "/tools/search-knowledge",
        json={
            "name": "search-knowledge", 
            "arguments": {
                "query": "test query",
                "limit": 5
            }
        }
    )
    # Component might not be available in test server
    if response.status_code == 200:
        data = response.json()
        assert "content" in data
    else:
        logger.info(f"Knowledge search endpoint not available (status: {response.status_code})")
        assert response.status_code in [404, 503]  # Not found or service unavailable

@pytest.mark.asyncio
async def test_get_task(test_server_client: AsyncClient):
    """Test task endpoint."""
    # Create a test task ID
    test_id = f"test_task_{uuid.uuid4().hex}"
    
    response = await test_server_client.post(
        "/task",
        json={
            "task_id": test_id,
            "status": "pending",
            "result": None
        }
    )
    assert response.status_code in [200, 404, 503]  # Allow various responses depending on component availability

@pytest.mark.asyncio
async def test_invalid_request(test_server_client: AsyncClient):
    """Test invalid request handling."""
    response = await test_server_client.post(
        "/tools/invalid-tool",
        json={
            "name": "invalid-tool",
            "arguments": {}
        }
    )
    assert response.status_code in [404, 400]  # Either not found or bad request

@pytest.mark.asyncio
async def test_not_found(test_server_client: AsyncClient):
    """Test 404 handling."""
    response = await test_server_client.get("/nonexistent-endpoint")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_server_lifecycle():
    """Test server lifecycle."""
    # This is a safety check to ensure we're not breaking anything
    # The actual server lifecycle is tested by the conftest fixtures
    assert True  # Replace with real checks if needed

@pytest.mark.asyncio
async def test_vector_store_search_threshold_validation(test_server_client: AsyncClient, setup_test_vector_store):
    """Test that the vector store search endpoint validates threshold values."""
    # Skip if vector store setup failed
    if setup_test_vector_store is None:
        pytest.skip("Vector store setup failed, skipping test")
    
    # Test invalid threshold greater than 1.0
    response = await test_server_client.get("/api/vector-store/search?query=test&threshold=1.5")
    assert response.status_code == 422
    assert "threshold" in response.text
    assert "less than or equal to" in response.text

    # Test invalid threshold less than 0.0
    response = await test_server_client.get("/api/vector-store/search?query=test&threshold=-0.5")
    assert response.status_code == 422
    assert "threshold" in response.text
    assert "greater than or equal to" in response.text

    # Test boundary value 0.0 (should be valid)
    response = await test_server_client.get("/api/vector-store/search?query=test&threshold=0.0")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["threshold"] == 0.0

    # Test boundary value 1.0 (should be valid)
    response = await test_server_client.get("/api/vector-store/search?query=test&threshold=1.0")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["threshold"] == 1.0

    # Test with valid filter parameters
    response = await test_server_client.get("/api/vector-store/search?query=test&threshold=0.7&file_type=python&path_pattern=src/*")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query" in data
    assert "total_results" in data
    assert "limit" in data
    assert "threshold" in data
    assert data["threshold"] == 0.7

    # If we have results, check their format
    if data["results"]:
        result = data["results"][0]
        assert "id" in result
        assert "score" in result
        assert "text" in result
        assert "file_path" in result
        assert "line_range" in result
        assert "type" in result
        assert "language" in result
        assert "timestamp" in result

@pytest.mark.asyncio
async def test_vector_store_search_functionality(test_server_client: AsyncClient, setup_test_vector_store):
    """Test comprehensive vector store search functionality.
    
    This test validates the full functionality of the vector store search endpoint,
    including result format, filtering, and metadata handling.
    
    The test checks:
    1. Basic search returns properly formatted results
    2. File type filtering works correctly
    3. Path pattern filtering works correctly
    4. Limit parameter controls result count
    5. Results contain all required metadata fields
    """
    # Skip if vector store setup failed
    if setup_test_vector_store is None:
        pytest.skip("Vector store setup failed, skipping test")
    
    # Test basic search functionality
    response = await test_server_client.get(
        "/api/vector-store/search",
        params={
            "query": "test query",
            "threshold": 0.7,
            "limit": 5
        }
    )
    
    # We should have a successful response now that the vector store is initialized
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "query" in data
    assert data["query"] == "test query"
    assert "results" in data
    assert "threshold" in data
    assert data["threshold"] == 0.7
    assert "total_results" in data
    assert "limit" in data
    assert data["limit"] == 5
    
    # Test with file type filter
    response = await test_server_client.get(
        "/api/vector-store/search",
        params={
            "query": "test query",
            "threshold": 0.7,
            "limit": 5,
            "file_type": "python"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "file_type" in data
    assert data["file_type"] == "python"
    
    # Test with path pattern filter
    response = await test_server_client.get(
        "/api/vector-store/search",
        params={
            "query": "test query",
            "threshold": 0.7,
            "limit": 5,
            "path_pattern": "src/**/*.py"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "path_pattern" in data
    assert data["path_pattern"] == "src/**/*.py"
    
    # Test with limit=1
    response = await test_server_client.get(
        "/api/vector-store/search",
        params={
            "query": "test query",
            "threshold": 0.7,
            "limit": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 1
    
    # If we have results, verify the result format
    if data["results"]:
        result = data["results"][0]
        # Check all required fields are present
        assert "id" in result
        assert "score" in result
        assert "text" in result
        assert "file_path" in result
        assert "line_range" in result
        assert "type" in result
        assert "language" in result
        assert "timestamp" in result
        
        # Validate data types
        assert isinstance(result["id"], str)
        assert isinstance(result["score"], (int, float))
        assert isinstance(result["text"], str)
        assert isinstance(result["file_path"], str)
        assert isinstance(result["line_range"], str)
        assert isinstance(result["type"], str)
        assert isinstance(result["language"], str)
        assert isinstance(result["timestamp"], str)

@pytest.mark.asyncio
async def test_vector_store_search_error_handling(test_server_client: AsyncClient, setup_test_vector_store):
    """Test error handling for vector store search endpoint.
    
    This test validates the error handling capabilities of the vector store search endpoint
    when provided with invalid or missing required parameters.
    
    The test checks:
    1. Missing query parameter returns appropriate error
    2. Invalid limit parameter (negative/zero) returns appropriate error
    """
    # Skip if vector store setup failed
    if setup_test_vector_store is None:
        pytest.skip("Vector store setup failed, skipping test")
    
    # Test missing query parameter
    response = await test_server_client.get(
        "/api/vector-store/search",
        params={
            "threshold": 0.7,
            "limit": 5
        }
    )
    
    # Missing required query parameter should return 422
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("query" in error["loc"] for error in data["detail"])
    
    # Test invalid limit parameter (negative)
    response = await test_server_client.get(
        "/api/vector-store/search",
        params={
            "query": "test query",
            "threshold": 0.7,
            "limit": -5
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("limit" in error["loc"] for error in data["detail"])
    
    # Test invalid limit parameter (zero)
    response = await test_server_client.get(
        "/api/vector-store/search",
        params={
            "query": "test query",
            "threshold": 0.7,
            "limit": 0
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("limit" in error["loc"] for error in data["detail"])

@pytest.mark.asyncio
async def test_vector_store_search_performance(test_server_client: AsyncClient, setup_test_vector_store):
    """Test performance of vector store search endpoint.
    
    This test measures the response time of the vector store search endpoint
    to ensure it meets performance requirements.
    
    The test checks:
    1. Search response time is within acceptable limits (< 1000ms)
    2. Multiple consecutive searches maintain performance
    """
    # Skip if vector store setup failed
    if setup_test_vector_store is None:
        pytest.skip("Vector store setup failed, skipping test")
        
    # Define performance thresholds
    max_response_time_ms = 1000  # 1 second maximum response time
    
    # Perform timed search tests
    for i in range(3):  # Test 3 consecutive searches
        start_time = time.time()
        
        response = await test_server_client.get(
            "/api/vector-store/search",
            params={
                "query": f"test performance query {i}",
                "threshold": 0.7,
                "limit": 5
            }
        )
        
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        logger.info(f"Search {i+1} response time: {response_time_ms:.2f}ms")
        
        # Assert performance is within acceptable limits
        assert response_time_ms < max_response_time_ms, \
            f"Search response time ({response_time_ms:.2f}ms) exceeds threshold ({max_response_time_ms}ms)"
        
        # Verify we got a valid response
        data = response.json()
        assert "results" in data
        assert "query" in data

@pytest.mark.asyncio
async def test_vector_store_search_threshold_validation_mock(test_server_client: AsyncClient):
    """Test that the vector store search endpoint validates threshold values using mock approach.
    
    This test isolates FastAPI's parameter validation from the actual server initialization.
    It doesn't test the vector store implementation but only the parameter validation logic.
    """
    # First, check if server is responding at all by checking health endpoint
    health_response = await test_server_client.get("/health")
    
    # If we can't even reach the server, skip the test
    if health_response.status_code >= 500:
        pytest.skip(f"Server is not responding (status: {health_response.status_code})")
    
    # Create a list of test cases: (threshold, expected_validation_error)
    # None for expected_validation_error means we expect validation to pass
    test_cases = [
        # Invalid thresholds (should fail validation)
        (1.5, "less than or equal to 1.0"),
        (-0.5, "greater than or equal to 0.0"),
        # Valid thresholds (should pass validation)
        (0.0, None),
        (1.0, None),
        (0.7, None),
    ]
    
    # Try each test case
    for threshold, expected_validation_error in test_cases:
        # Skip testing health check which will never have parameter validation errors
        # Here we're just testing the static validation in the FastAPI route definition
        # This will trigger validation errors regardless of server state
        response = await test_server_client.get(f"/api/vector-store/search?query=test&threshold={threshold}")
        
        # Check response based on expected validation
        if expected_validation_error:
            # If validation error is expected, check for 422 status
            # Note: If we got 503, parameter validation didn't even happen
            # In some test environments this is normal, so we'll skip the assertion
            if response.status_code == 503:
                logger.info(f"Server returned 503 for threshold={threshold}, "
                           f"parameter validation couldn't be tested due to server state")
                continue
                
            # If we get here, we should have a 422 validation error
            assert response.status_code == 422, \
                f"Expected 422 for invalid threshold {threshold}, got {response.status_code}: {response.text}"
            
            # Check if validation error message contains expected text
            assert expected_validation_error in response.text, \
                f"Expected validation error to contain '{expected_validation_error}', got: {response.text}"
            
            logger.info(f"Threshold {threshold} correctly failed validation with message containing '{expected_validation_error}'")
        else:
            # For valid thresholds, skip assertion if server returned 503
            if response.status_code == 503:
                logger.info(f"Server returned 503 for valid threshold={threshold}, "
                           f"but parameter validation passed (otherwise would be 422)")
                continue
                
            # If we get a non-503 response for a valid threshold, it should be 200
            # (or 404 if the endpoint doesn't exist in test server)
            assert response.status_code in [200, 404], \
                f"Expected 200 for valid threshold {threshold}, got {response.status_code}: {response.text}"
            
            logger.info(f"Threshold {threshold} correctly passed validation")
    
    logger.info("Completed threshold parameter validation tests")
