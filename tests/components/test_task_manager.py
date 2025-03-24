import pytest
from pathlib import Path
from typing import AsyncGenerator
from mcp_codebase_insight.core.tasks import TaskManager, TaskType, TaskStatus
from mcp_codebase_insight.core.config import ServerConfig

@pytest.fixture
async def task_manager(test_config: ServerConfig):
    manager = TaskManager(test_config)
    await manager.initialize()
    yield manager
    await manager.cleanup()

@pytest.mark.asyncio
async def test_task_manager_initialization(task_manager: TaskManager):
    """Test that task manager initializes correctly."""
    assert task_manager is not None
    assert task_manager.config is not None

@pytest.mark.asyncio
async def test_create_and_get_task(task_manager: TaskManager, test_code: str):
    """Test creating and retrieving tasks."""
    # Create task
    task = await task_manager.create_task(
        type="code_analysis",
        title="Test task",
        description="Test task description",
        context={"code": test_code}
    )
    assert task is not None
    
    # Get task
    retrieved_task = await task_manager.get_task(task.id)
    assert retrieved_task.context["code"] == test_code
    assert retrieved_task.type == TaskType.CODE_ANALYSIS
    assert retrieved_task.description == "Test task description"

@pytest.mark.asyncio
async def test_task_status_updates(task_manager: TaskManager, test_code: str):
    """Test task status updates."""
    # Create task
    task = await task_manager.create_task(
        type="code_analysis",
        title="Status Test",
        description="Test task status updates",
        context={"code": test_code}
    )
    
    # Update status
    await task_manager.update_task(task.id, status=TaskStatus.IN_PROGRESS)
    updated_task = await task_manager.get_task(task.id)
    assert updated_task.status == TaskStatus.IN_PROGRESS
    
    await task_manager.update_task(task.id, status=TaskStatus.COMPLETED)
    completed_task = await task_manager.get_task(task.id)
    assert completed_task.status == TaskStatus.COMPLETED

@pytest.mark.asyncio
async def test_task_result_updates(task_manager: TaskManager, test_code: str):
    """Test updating task results."""
    # Create task
    task = await task_manager.create_task(
        type="code_analysis",
        title="Result Test",
        description="Test task result updates",
        context={"code": test_code}
    )
    
    # Update result
    result = {"analysis": "Test analysis result"}
    await task_manager.update_task(task.id, result=result)
    
    # Verify result
    updated_task = await task_manager.get_task(task.id)
    assert updated_task.result == result

@pytest.mark.asyncio
async def test_list_tasks(task_manager: TaskManager, test_code: str):
    """Test listing tasks."""
    # Create multiple tasks
    tasks = []
    for i in range(3):
        task = await task_manager.create_task(
            type="code_analysis",
            title=f"List Test {i}",
            description=f"Test task {i}",
            context={"code": test_code}
        )
        tasks.append(task)
    
    # List tasks
    task_list = await task_manager.list_tasks()
    assert len(task_list) >= 3
    
    # Verify task descriptions
    descriptions = [task.description for task in task_list]
    for i in range(3):
        assert f"Test task {i}" in descriptions 