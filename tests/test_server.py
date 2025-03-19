"""Tests for MCP server."""

import pytest
from fastapi.testclient import TestClient
import json
from typing import Dict, Any

from src.mcp_server_qdrant.server import CodebaseAnalysisServer
from src.mcp_server_qdrant.core.config import ServerConfig

@pytest.fixture
def server(test_config: ServerConfig) -> CodebaseAnalysisServer:
    """Create test server."""
    return CodebaseAnalysisServer(test_config)

@pytest.fixture
def client(server: CodebaseAnalysisServer) -> TestClient:
    """Create test client."""
    return TestClient(server.mcp.app)

def test_server_info(client: TestClient):
    """Test server info endpoint."""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "example-codebase-analysis"
    assert "version" in data

def test_list_tools(client: TestClient):
    """Test listing available tools."""
    response = client.get("/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    tools = data["tools"]
    assert len(tools) > 0
    assert all("name" in tool and "description" in tool for tool in tools)

@pytest.mark.asyncio
async def test_analyze_code(client: TestClient):
    """Test code analysis tool."""
    code = """
    def process_data(data):
        results = []
        for item in data:
            if item.get('active'):
                value = item.get('value', 0)
                if value > 100:
                    results.append(value * 2)
        return results
    """
    
    response = client.post(
        "/tools/analyze-code",
        json={
            "code": code,
            "context": {
                "language": "python",
                "purpose": "data processing"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    
    # Check task status
    task_response = client.get(f"/tools/get-task?task_id={data['task_id']}")
    assert task_response.status_code == 200
    task_data = task_response.json()
    assert task_data["type"] == "code_analysis"
    assert task_data["status"] in ["completed", "in_progress"]

@pytest.mark.asyncio
async def test_create_adr(client: TestClient):
    """Test ADR creation tool."""
    response = client.post(
        "/tools/create-adr",
        json={
            "title": "Test ADR",
            "context": {
                "technical": "Test technical context",
                "business": "Test business context"
            },
            "options": [
                {
                    "name": "Option 1",
                    "description": "First option",
                    "pros": ["Pro 1"],
                    "cons": ["Con 1"]
                },
                {
                    "name": "Option 2",
                    "description": "Second option",
                    "pros": ["Pro 2"],
                    "cons": ["Con 2"]
                }
            ],
            "decision": "Selected Option 1"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "adr_path" in data

@pytest.mark.asyncio
async def test_debug_issue(client: TestClient):
    """Test debug issue tool."""
    response = client.post(
        "/tools/debug-issue",
        json={
            "description": "Test issue",
            "type": "performance",
            "context": {
                "symptoms": "Test symptoms",
                "environment": "Test environment"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "steps" in data

@pytest.mark.asyncio
async def test_search_knowledge(client: TestClient):
    """Test knowledge base search tool."""
    response = client.post(
        "/tools/search-knowledge",
        json={
            "query": "python error handling",
            "type": "best_practice",
            "limit": 3
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "patterns" in data
    patterns = data["patterns"]
    assert len(patterns) <= 3
    assert all(
        "id" in p and "name" in p and "description" in p
        for p in patterns
    )

@pytest.mark.asyncio
async def test_crawl_docs(client: TestClient):
    """Test documentation crawling tool."""
    response = client.post(
        "/tools/crawl-docs",
        json={
            "urls": ["https://example.com/docs"],
            "source_type": "api"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data

def test_error_handling(client: TestClient):
    """Test error handling in server."""
    # Test invalid tool
    response = client.post("/tools/invalid-tool")
    assert response.status_code == 404
    
    # Test invalid parameters
    response = client.post(
        "/tools/analyze-code",
        json={"invalid": "params"}
    )
    assert response.status_code == 422
    
    # Test missing required parameters
    response = client.post(
        "/tools/create-adr",
        json={
            "title": "Test ADR"
            # Missing required fields
        }
    )
    assert response.status_code == 422

def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "components" in data
    assert "system" in data

def test_metrics(client: TestClient):
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Check for core metrics
    assert "task_count" in data
    assert "vector_store_query_count" in data
    assert "cache_hit_count" in data
