"""Test core server components."""

import pytest
from datetime import datetime
from uuid import uuid4

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.adr import ADRManager, ADRStatus
from mcp_codebase_insight.core.debug import DebugSystem, IssueType, IssueStatus
from mcp_codebase_insight.core.documentation import DocumentationManager, DocumentationType
from mcp_codebase_insight.core.knowledge import KnowledgeBase, Pattern, PatternType, PatternConfidence
from mcp_codebase_insight.core.tasks import TaskManager, TaskType, TaskStatus, TaskPriority
from mcp_codebase_insight.core.metrics import MetricsManager, MetricType
from mcp_codebase_insight.core.health import HealthManager, HealthStatus
from mcp_codebase_insight.core.cache import CacheManager
from mcp_codebase_insight.core.vector_store import VectorStore
from mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding

@pytest.mark.asyncio
async def test_adr_manager(test_config: ServerConfig, test_adr: dict):
    """Test ADR manager functions."""
    manager = ADRManager(test_config)
    
    # Test creation
    adr = await manager.create_adr(
        title=test_adr["title"],
        context=test_adr["context"],
        options=test_adr["options"],
        decision=test_adr["decision"]
    )
    
    assert adr.title == test_adr["title"]
    assert adr.status == ADRStatus.PROPOSED
    
    # Test retrieval
    retrieved = await manager.get_adr(adr.id)
    assert retrieved is not None
    assert retrieved.id == adr.id
    
    # Test update
    updated = await manager.update_adr(
        adr.id,
        status=ADRStatus.ACCEPTED
    )
    assert updated.status == ADRStatus.ACCEPTED

@pytest.mark.asyncio
async def test_knowledge_base(test_config: ServerConfig, qdrant_client):
    """Test knowledge base functions."""
    # Initialize vector store with embedder
    embedder = SentenceTransformerEmbedding()
    vector_store = VectorStore(
        url=test_config.qdrant_url,
        embedder=embedder
    )
    kb = KnowledgeBase(test_config, vector_store=vector_store)
    
    # Test pattern creation
    now = datetime.utcnow()
    pattern = Pattern(
        id=uuid4(),
        name="Test Pattern",
        description="A test pattern",
        type=PatternType.CODE,
        content="def test(): pass",
        confidence=PatternConfidence.HIGH,
        created_at=now,
        updated_at=now
    )
    
    # Test pattern storage
    stored_pattern = await kb.add_pattern(
        name=pattern.name,
        type=pattern.type,
        description=pattern.description,
        content=pattern.content,
        confidence=pattern.confidence
    )
    
    # Verify stored pattern
    assert stored_pattern.name == pattern.name
    assert stored_pattern.type == pattern.type
    assert stored_pattern.description == pattern.description
    assert stored_pattern.content == pattern.content
    assert stored_pattern.confidence == pattern.confidence

@pytest.mark.asyncio
async def test_task_manager(test_config: ServerConfig, test_code: str):
    """Test task manager functions."""
    manager = TaskManager(
        config=test_config,
        adr_manager=ADRManager(test_config),
        debug_system=DebugSystem(test_config),
        doc_manager=DocumentationManager(test_config),
        knowledge_base=KnowledgeBase(test_config, None),
        prompt_manager=None
    )
    
    # Test task creation
    task = await manager.create_task(
        type=TaskType.CODE_ANALYSIS,
        title="Test Task",
        description="Analyze test code",
        priority=TaskPriority.MEDIUM,
        context={"code": test_code}
    )
    
    assert task.title == "Test Task"
    assert task.status == TaskStatus.PENDING
    
    # Test task retrieval
    retrieved = await manager.get_task(task.id)
    assert retrieved is not None
    assert retrieved.id == task.id

@pytest.mark.asyncio
async def test_metrics_manager(test_config: ServerConfig):
    """Test metrics manager functions."""
    # Override the metrics_enabled setting for this test
    test_config.metrics_enabled = True
    
    manager = MetricsManager(test_config)
    await manager.initialize()
    
    try:
        # Test metric recording
        await manager.record_metric(
            "test_metric",
            MetricType.COUNTER,
            1.0,
            {"label": "test"}
        )
        
        # Test metric retrieval
        metrics = await manager.get_metrics(["test_metric"])
        assert len(metrics) == 1
        assert "test_metric" in metrics
    finally:
        # Cleanup
        await manager.cleanup()

@pytest.mark.asyncio
async def test_health_manager(test_config: ServerConfig):
    """Test health manager functions."""
    manager = HealthManager(test_config)
    
    # Test health check
    health = await manager.check_health()
    assert health.status is not None
    assert isinstance(health.components, dict)
    assert isinstance(health.timestamp, datetime)

@pytest.mark.asyncio
async def test_cache_manager(test_config: ServerConfig):
    """Test cache manager functions."""
    manager = CacheManager(test_config)
    await manager.initialize()  # Initialize the manager
    
    try:
        # Test memory cache
        manager.put_in_memory("test_key", "test_value")
        result = manager.get_from_memory("test_key")
        assert result == "test_value"
        
        # Test persistent cache
        manager.put_in_disk("test_key", "test_value")
        result = manager.get_from_disk("test_key")
        assert result == "test_value"
        
        # Test combined operations
        manager.put("combined_key", "combined_value")
        result = manager.get("combined_key")
        assert result == "combined_value"
        
        # Test removal
        manager.remove("test_key")
        assert manager.get("test_key") is None
    finally:
        await manager.cleanup()  # Clean up after tests

@pytest.mark.asyncio
async def test_documentation_manager(test_config: ServerConfig):
    """Test documentation manager functions."""
    manager = DocumentationManager(test_config)
    
    # Test document creation
    doc = await manager.add_document(
        title="Test Doc",
        content="Test content",
        type=DocumentationType.REFERENCE
    )
    
    assert doc.title == "Test Doc"
    
    # Test document retrieval
    retrieved = await manager.get_document(doc.id)
    assert retrieved is not None
    assert retrieved.id == doc.id

@pytest.mark.asyncio
async def test_debug_system(test_config: ServerConfig):
    """Test debug system functions."""
    system = DebugSystem(test_config)
    
    # Test issue creation
    issue = await system.create_issue(
        title="Test issue",
        type=IssueType.BUG,
        description={"message": "Test description", "steps": ["Step 1", "Step 2"]}
    )
    
    assert issue.title == "Test issue"
    assert issue.type == IssueType.BUG
    assert issue.status == IssueStatus.OPEN
    assert "message" in issue.description
    assert "steps" in issue.description
