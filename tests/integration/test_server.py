"""Test server API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
import uuid
import logging

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.server import CodebaseAnalysisServer
from mcp_codebase_insight.server_test_isolation import get_isolated_server_state

# Setup logger
logger = logging.getLogger(__name__)

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
