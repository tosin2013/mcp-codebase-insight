import pytest

@pytest.mark.asyncio
async def test_create_file_relationship(test_client):
    """Test creating a file relationship."""
    relationship_data = {
        "source_file": "src/main.py",
        "target_file": "src/utils.py",
        "relationship_type": "imports",
        "description": "Main imports utility functions",
        "metadata": {"importance": "high"}
    }
    
    response = await test_client.post("/relationships", json=relationship_data)
    assert response.status_code == 200
    data = response.json()
    assert data["source_file"] == relationship_data["source_file"]
    assert data["target_file"] == relationship_data["target_file"]
    assert data["relationship_type"] == relationship_data["relationship_type"]

@pytest.mark.asyncio
async def test_get_file_relationships(test_client):
    """Test getting file relationships."""
    # Create a test relationship first
    relationship_data = {
        "source_file": "src/test.py",
        "target_file": "src/helper.py",
        "relationship_type": "depends_on"
    }
    await test_client.post("/relationships", json=relationship_data)
    
    # Test getting all relationships
    response = await test_client.get("/relationships")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)
    
    # Test filtering by source file
    response = await test_client.get("/relationships", params={"source_file": "src/test.py"})
    assert response.status_code == 200
    data = response.json()
    assert all(r["source_file"] == "src/test.py" for r in data)

@pytest.mark.asyncio
async def test_create_web_source(test_client):
    """Test creating a web source."""
    source_data = {
        "url": "https://example.com/docs",
        "title": "API Documentation",
        "content_type": "documentation",
        "description": "External API documentation",
        "tags": ["api", "docs"],
        "metadata": {"version": "1.0"}
    }
    
    response = await test_client.post("/web-sources", json=source_data)
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == source_data["url"]
    assert data["title"] == source_data["title"]
    assert data["content_type"] == source_data["content_type"]

@pytest.mark.asyncio
async def test_get_web_sources(test_client):
    """Test getting web sources."""
    # Create a test web source first
    source_data = {
        "url": "https://example.com/tutorial",
        "title": "Tutorial",
        "content_type": "tutorial",
        "tags": ["guide", "tutorial"]
    }
    await test_client.post("/web-sources", json=source_data)
    
    # Test getting all web sources
    response = await test_client.get("/web-sources")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)
    
    # Test filtering by content type
    response = await test_client.get("/web-sources", params={"content_type": "tutorial"})
    assert response.status_code == 200
    data = response.json()
    assert all(s["content_type"] == "tutorial" for s in data)
    
    # Test filtering by tags
    response = await test_client.get("/web-sources", params={"tags": ["guide"]})
    assert response.status_code == 200
    data = response.json()
    assert any("guide" in s["tags"] for s in data) 