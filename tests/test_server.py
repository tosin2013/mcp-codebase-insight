"""Test server API endpoints."""

import pytest
from fastapi.testclient import TestClient

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.server import CodebaseAnalysisServer

def test_health_check(test_client: TestClient):
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_metrics(test_client: TestClient):
    """Test metrics endpoint."""
    response = test_client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_analyze_code(test_client: TestClient, test_code: str):
    """Test code analysis endpoint."""
    response = test_client.post(
        "/tools/analyze-code",
        json={
            "name": "analyze-code",
            "arguments": {
                "code": test_code,
                "context": {}
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["isError"]
    assert len(data["content"]) > 0
    assert "task_id" in data["content"][0]

def test_create_adr(test_client: TestClient, test_adr: dict):
    """Test ADR creation endpoint."""
    response = test_client.post(
        "/tools/create-adr",
        json={
            "name": "create-adr",
            "arguments": {
                "title": test_adr["title"],
                "context": test_adr["context"],
                "options": test_adr["options"],
                "decision": test_adr["decision"]
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["isError"]
    assert "task_id" in data["content"][0]
    assert "adr_path" in data["content"][0]

def test_debug_issue(test_client: TestClient):
    """Test issue debugging endpoint."""
    response = test_client.post(
        "/tools/debug-issue",
        json={
            "name": "debug-issue",
            "arguments": {
                "description": "Test issue description",
                "type": "bug",
                "context": {
                    "severity": "medium"
                }
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["isError"]
    assert "task_id" in data["content"][0]
    assert "steps" in data["content"][0]

def test_search_knowledge(test_client: TestClient):
    """Test knowledge base search endpoint."""
    response = test_client.post(
        "/tools/search-knowledge",
        json={
            "name": "search-knowledge",
            "arguments": {
                "query": "error handling patterns",
                "type": "code",
                "limit": 5
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["isError"]
    assert isinstance(data["content"], list)

def test_get_task(test_client: TestClient, test_code: str):
    """Test task status retrieval endpoint."""
    # First create a task
    response = test_client.post(
        "/tools/analyze-code",
        json={
            "name": "analyze-code",
            "arguments": {
                "code": test_code,
                "context": {}
            }
        }
    )
    task_id = response.json()["content"][0]["task_id"]
    
    # Then get its status
    response = test_client.post(
        "/tools/get-task",
        json={
            "name": "get-task",
            "arguments": {
                "task_id": task_id
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["isError"]
    assert data["content"][0]["task_id"] == task_id
    assert "status" in data["content"][0]
    assert "result" in data["content"][0]

def test_invalid_request(test_client: TestClient):
    """Test error handling for invalid requests."""
    response = test_client.post(
        "/tools/analyze-code",
        json={
            "name": "analyze-code",
            "arguments": {}  # Missing required arguments
        }
    )
    assert response.status_code in [400, 422]
    data = response.json()
    assert "detail" in data
    assert "missing required field" in data["detail"].lower()

def test_not_found(test_client: TestClient):
    """Test handling of non-existent endpoints."""
    response = test_client.get("/nonexistent")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_server_lifecycle(test_config: ServerConfig):
    """Test server startup and shutdown."""
    server = CodebaseAnalysisServer(test_config)
    
    # Test graceful shutdown
    await server.stop()
    
    # Ensure we can create a new instance after shutdown
    new_server = CodebaseAnalysisServer(test_config)
    assert new_server is not None
