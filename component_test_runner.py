#!/usr/bin/env python
"""
Component Test Runner

A specialized runner for executing component tests with proper async fixture handling.
This bypasses the standard pytest fixture mechanisms to handle async fixtures correctly
in isolated execution environments.
"""
import os
import sys
import uuid
import asyncio
import importlib
from pathlib import Path
import inspect
import logging
import re
from typing import Dict, Any, List, Callable, Tuple, Optional, Set, Awaitable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("component-test-runner")

# Import the sys module to modify path
import sys
sys.path.insert(0, '/Users/tosinakinosho/workspaces/mcp-codebase-insight')

# Import required components directly to avoid fixture resolution issues
from src.mcp_codebase_insight.core.config import ServerConfig
from src.mcp_codebase_insight.core.vector_store import VectorStore
from src.mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding
from src.mcp_codebase_insight.core.knowledge import KnowledgeBase
from src.mcp_codebase_insight.core.tasks import TaskManager


async def create_test_config() -> ServerConfig:
    """Create a server configuration for tests."""
    # Generate a unique collection name for this test run
    collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"
    
    # Check if MCP_COLLECTION_NAME is set in env, use that instead if available
    if "MCP_COLLECTION_NAME" in os.environ:
        collection_name = os.environ["MCP_COLLECTION_NAME"]
    
    logger.info(f"Using test collection: {collection_name}")
    
    config = ServerConfig(
        host="localhost",
        port=8000,
        log_level="DEBUG",
        qdrant_url="http://localhost:6333",
        docs_cache_dir=Path(".test_cache") / "docs",
        adr_dir=Path(".test_cache") / "docs/adrs",
        kb_storage_dir=Path(".test_cache") / "knowledge",
        embedding_model="all-MiniLM-L6-v2",
        collection_name=collection_name,
        debug_mode=True,
        metrics_enabled=False,
        cache_enabled=True,
        memory_cache_size=1000,
        disk_cache_dir=Path(".test_cache") / "cache"
    )
    return config


async def create_embedder() -> SentenceTransformerEmbedding:
    """Create an embedder for tests."""
    logger.info("Initializing the embedder...")
    return SentenceTransformerEmbedding()


async def create_vector_store(config: ServerConfig, embedder: SentenceTransformerEmbedding) -> VectorStore:
    """Create a vector store for tests."""
    logger.info("Initializing the vector store...")
    store = VectorStore(config.qdrant_url, embedder)
    try:
        await store.initialize()
        logger.info("Vector store initialized successfully")
        return store
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        raise RuntimeError(f"Failed to initialize vector store: {e}")


async def create_knowledge_base(config: ServerConfig, vector_store: VectorStore) -> KnowledgeBase:
    """Create a knowledge base for tests."""
    logger.info("Initializing the knowledge base...")
    kb = KnowledgeBase(config, vector_store)
    try:
        await kb.initialize()
        logger.info("Knowledge base initialized successfully")
        return kb
    except Exception as e:
        logger.error(f"Failed to initialize knowledge base: {e}")
        raise RuntimeError(f"Failed to initialize knowledge base: {e}")


async def create_task_manager(config: ServerConfig) -> TaskManager:
    """Create a task manager for tests."""
    logger.info("Initializing the task manager...")
    manager = TaskManager(config)
    try:
        await manager.initialize()
        logger.info("Task manager initialized successfully")
        return manager
    except Exception as e:
        logger.error(f"Failed to initialize task manager: {e}")
        raise RuntimeError(f"Failed to initialize task manager: {e}")


async def create_test_metadata() -> Dict[str, Any]:
    """Standard test metadata for consistency across tests."""
    return {
        "type": "code",
        "language": "python",
        "title": "Test Code",
        "description": "Test code snippet for vector store testing",
        "tags": ["test", "vector"]
    }


def create_test_code() -> str:
    """Provide sample code for testing task-related functionality."""
    return """
def example_function():
    \"\"\"This is a test function for task manager tests.\"\"\"
    return "Hello, world!"

class TestClass:
    def __init__(self):
        self.value = 42
        
    def method(self):
        return self.value
"""


async def cleanup_vector_store(vector_store: VectorStore) -> None:
    """Cleanup a vector store after tests."""
    if vector_store and hasattr(vector_store, 'cleanup'):
        logger.info("Cleaning up vector store...")
        try:
            await vector_store.cleanup()
            logger.info("Vector store cleanup completed")
        except Exception as e:
            logger.error(f"Error during vector store cleanup: {e}")


async def cleanup_knowledge_base(kb: KnowledgeBase) -> None:
    """Cleanup a knowledge base after tests."""
    if kb and hasattr(kb, 'cleanup'):
        logger.info("Cleaning up knowledge base...")
        try:
            await kb.cleanup()
            logger.info("Knowledge base cleanup completed")
        except Exception as e:
            logger.error(f"Error during knowledge base cleanup: {e}")


async def cleanup_task_manager(manager: TaskManager) -> None:
    """Cleanup a task manager after tests."""
    if manager and hasattr(manager, 'cleanup'):
        logger.info("Cleaning up task manager...")
        try:
            await manager.cleanup()
            logger.info("Task manager cleanup completed")
        except Exception as e:
            logger.error(f"Error cleaning up task manager: {e}")


def get_module_tests(module_path: str) -> List[str]:
    """Get the list of tests in a module."""
    logger.info(f"Analyzing module: {module_path}")
    with open(module_path, 'r') as file:
        content = file.read()
    
    # Pattern to match test functions but exclude fixtures
    pattern = r'async\s+def\s+(test_\w+)\s*\('
    
    # Find test functions that are not fixtures (exclude lines with @pytest.fixture)
    lines = content.split('\n')
    test_functions = []
    
    for i, line in enumerate(lines):
        if i > 0 and '@pytest.fixture' in lines[i-1]:
            continue  # Skip this as it's a fixture, not a test
        
        match = re.search(pattern, line)
        if match:
            test_functions.append(match.group(1))
    
    logger.info(f"Found {len(test_functions)} tests in {module_path}")
    return test_functions

def load_test_module(module_path: str):
    """Load a test module with proper path handling."""
    # Convert file path to module path
    if module_path.endswith('.py'):
        module_path = module_path[:-3]  # Remove .py extension
    
    # Convert path separators to module separators
    module_name = module_path.replace('/', '.').replace('\\', '.')
    
    # Ensure we use the correct Python path
    if not any(p == '.' for p in sys.path):
        sys.path.append('.')
    
    logger.info(f"Attempting to import module: {module_name}")
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        logger.error(f"Failed to import test module {module_name}: {e}")
        return None


async def run_component_test(module_path: str, test_name: str) -> bool:
    """
    Dynamically load and run a component test with proper fixture initialization.
    
    Args:
        module_path: Path to the test module
        test_name: Name of the test function to run
        
    Returns:
        True if test passed, False if it failed
    """
    logger.info(f"Running test: {module_path}::{test_name}")
    
    # Import the test module
    test_module = load_test_module(module_path)
    if not test_module:
        return False
    
    # Get the test function
    if not hasattr(test_module, test_name):
        logger.error(f"Test function {test_name} not found in module {module_name}")
        return False
    
    test_func = getattr(test_module, test_name)
    
    # Determine which fixtures the test needs
    required_fixtures = inspect.signature(test_func).parameters
    logger.info(f"Test requires fixtures: {list(required_fixtures.keys())}")
    
    # Initialize the required fixtures
    fixture_values = {}
    resources_to_cleanup = []
    
    try:
        # Create ServerConfig first since many other fixtures depend on it
        if "test_config" in required_fixtures:
            logger.info("Setting up test_config fixture")
            fixture_values["test_config"] = await create_test_config()
        
        # Create embedder if needed
        if "embedder" in required_fixtures:
            logger.info("Setting up embedder fixture")
            fixture_values["embedder"] = await create_embedder()
        
        # Create test metadata if needed
        if "test_metadata" in required_fixtures:
            logger.info("Setting up test_metadata fixture")
            fixture_values["test_metadata"] = await create_test_metadata()
        
        # Create test code if needed
        if "test_code" in required_fixtures:
            logger.info("Setting up test_code fixture")
            fixture_values["test_code"] = create_test_code()
        
        # Create vector store if needed
        if "vector_store" in required_fixtures:
            logger.info("Setting up vector_store fixture")
            if "test_config" not in fixture_values:
                fixture_values["test_config"] = await create_test_config()
            if "embedder" not in fixture_values:
                fixture_values["embedder"] = await create_embedder()
            
            fixture_values["vector_store"] = await create_vector_store(
                fixture_values["test_config"], 
                fixture_values["embedder"]
            )
            resources_to_cleanup.append(("vector_store", fixture_values["vector_store"]))
        
        # Create knowledge base if needed
        if "knowledge_base" in required_fixtures:
            logger.info("Setting up knowledge_base fixture")
            if "test_config" not in fixture_values:
                fixture_values["test_config"] = await create_test_config()
            if "vector_store" not in fixture_values:
                if "embedder" not in fixture_values:
                    fixture_values["embedder"] = await create_embedder()
                fixture_values["vector_store"] = await create_vector_store(
                    fixture_values["test_config"], 
                    fixture_values["embedder"]
                )
                resources_to_cleanup.append(("vector_store", fixture_values["vector_store"]))
            
            fixture_values["knowledge_base"] = await create_knowledge_base(
                fixture_values["test_config"], 
                fixture_values["vector_store"]
            )
            resources_to_cleanup.append(("knowledge_base", fixture_values["knowledge_base"]))
        
        # Create task manager if needed
        if "task_manager" in required_fixtures:
            logger.info("Setting up task_manager fixture")
            if "test_config" not in fixture_values:
                fixture_values["test_config"] = await create_test_config()
            
            fixture_values["task_manager"] = await create_task_manager(fixture_values["test_config"])
            resources_to_cleanup.append(("task_manager", fixture_values["task_manager"]))
        
        # Ensure all required fixtures are initialized
        missing_fixtures = set(required_fixtures.keys()) - set(fixture_values.keys())
        if missing_fixtures:
            logger.error(f"Missing required fixtures: {missing_fixtures}")
            return False
        
        # Run the actual test
        logger.info(f"Executing test with fixtures: {list(fixture_values.keys())}")
        test_kwargs = {name: value for name, value in fixture_values.items() if name in required_fixtures}
        
        # Check if the test function is an async function
        if inspect.iscoroutinefunction(test_func):
            # For async test functions, await them
            logger.info(f"Running async test: {test_name}")
            await test_func(**test_kwargs)
        else:
            # For regular test functions, just call them
            logger.info(f"Running synchronous test: {test_name}")
            test_func(**test_kwargs)
        
        logger.info(f"Test {test_name} completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Test {test_name} failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        # Clean up resources in reverse order (LIFO)
        logger.info("Cleaning up resources...")
        for resource_type, resource in reversed(resources_to_cleanup):
            try:
                if resource_type == "vector_store":
                    await cleanup_vector_store(resource)
                elif resource_type == "knowledge_base":
                    await cleanup_knowledge_base(resource)
                elif resource_type == "task_manager":
                    await cleanup_task_manager(resource)
            except Exception as e:
                logger.error(f"Error cleaning up {resource_type}: {e}")


def main():
    """Run a component test with proper async fixture handling."""
    if len(sys.argv) < 2:
        print("Usage: python component_test_runner.py <module_path> <test_name>")
        sys.exit(1)
    
    module_path = sys.argv[1]
    
    # Configure event loop policy for macOS if needed
    if sys.platform == 'darwin':
        import platform
        if int(platform.mac_ver()[0].split('.')[0]) >= 10:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    try:
        if len(sys.argv) < 3:
            # No specific test provided, use module discovery
            tests = get_module_tests(module_path)
            if not tests:
                logger.error(f"No tests found in {module_path}")
                sys.exit(1)
            
            # Run all tests in the module
            successful_tests = 0
            for test_name in tests:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                test_result = loop.run_until_complete(run_component_test(module_path, test_name))
                loop.close()
                if test_result:
                    successful_tests += 1
            
            # Report test results
            logger.info(f"Test Results: {successful_tests}/{len(tests)} tests passed")
            sys.exit(0 if successful_tests == len(tests) else 1)
        else:
            # Run a specific test
            test_name = sys.argv[2]
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(run_component_test(module_path, test_name))
            loop.close()
            sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Test execution interrupted")
        sys.exit(130)  # 130 is the standard exit code for SIGINT
    except Exception as e:
        logger.error(f"Unhandled exception during test execution: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
