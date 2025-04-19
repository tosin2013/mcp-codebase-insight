# MCP Codebase Insight Cookbook

This cookbook provides practical examples, common use cases, and solutions for working with the MCP Codebase Insight system. Each recipe includes step-by-step instructions, code examples, and explanations.

## Table of Contents

- [Setup and Configuration](#setup-and-configuration)
- [Vector Store Operations](#vector-store-operations)
- [Code Analysis](#code-analysis)
- [Knowledge Base Integration](#knowledge-base-integration)
- [Task Management](#task-management)
- [Transport Protocol Usage](#transport-protocol-usage)
- [Troubleshooting](#troubleshooting)

## Setup and Configuration

### Recipe: Quick Start Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/mcp-codebase-insight.git
cd mcp-codebase-insight

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Recipe: Configure Vector Store

```python
from mcp_codebase_insight.core.vector_store import VectorStore
from mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding

async def setup_vector_store():
    # Initialize embedder
    embedder = SentenceTransformerEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    await embedder.initialize()
    
    # Initialize vector store
    vector_store = VectorStore(
        url="http://localhost:6333",
        embedder=embedder,
        collection_name="mcp-codebase-insight",
        api_key="your-api-key",  # Optional
        vector_name="default"
    )
    await vector_store.initialize()
    return vector_store
```

## Vector Store Operations

### Recipe: Store and Search Code Snippets

```python
async def store_code_snippet(vector_store, code: str, metadata: dict):
    await vector_store.add_vector(
        text=code,
        metadata={
            "type": "code",
            "content": code,
            **metadata
        }
    )

async def search_similar_code(vector_store, query: str, limit: int = 5):
    results = await vector_store.search_similar(
        query=query,
        limit=limit
    )
    return results

# Usage example
code_snippet = """
def calculate_sum(a: int, b: int) -> int:
    return a + b
"""

metadata = {
    "filename": "math_utils.py",
    "function_name": "calculate_sum",
    "language": "python"
}

await store_code_snippet(vector_store, code_snippet, metadata)
similar_snippets = await search_similar_code(vector_store, "function to add two numbers")
```

### Recipe: Batch Processing Code Files

```python
import asyncio
from pathlib import Path

async def process_codebase(vector_store, root_dir: str):
    async def process_file(file_path: Path):
        if not file_path.suffix == '.py':  # Adjust for your needs
            return
            
        code = file_path.read_text()
        await store_code_snippet(vector_store, code, {
            "filename": file_path.name,
            "path": str(file_path),
            "language": "python"
        })

    root = Path(root_dir)
    tasks = [
        process_file(f) 
        for f in root.rglob('*') 
        if f.is_file()
    ]
    await asyncio.gather(*tasks)
```

## Code Analysis

### Recipe: Detect Architectural Patterns

```python
from mcp_codebase_insight.analysis.patterns import PatternDetector

async def analyze_architecture(code_path: str):
    detector = PatternDetector()
    patterns = await detector.detect_patterns(code_path)
    
    for pattern in patterns:
        print(f"Pattern: {pattern.name}")
        print(f"Location: {pattern.location}")
        print(f"Confidence: {pattern.confidence}")
        print("---")
```

### Recipe: Generate Code Insights

```python
from mcp_codebase_insight.analysis.insights import InsightGenerator

async def generate_insights(vector_store, codebase_path: str):
    generator = InsightGenerator(vector_store)
    insights = await generator.analyze_codebase(codebase_path)
    
    return {
        "complexity_metrics": insights.complexity,
        "dependency_graph": insights.dependencies,
        "architectural_patterns": insights.patterns,
        "recommendations": insights.recommendations
    }
```

## Knowledge Base Integration

### Recipe: Store and Query Documentation

```python
from mcp_codebase_insight.kb.store import KnowledgeBase

async def manage_documentation(kb: KnowledgeBase):
    # Store documentation
    await kb.store_document(
        content="API documentation content...",
        metadata={
            "type": "api_doc",
            "version": "1.0",
            "category": "reference"
        }
    )
    
    # Query documentation
    results = await kb.search(
        query="How to configure authentication",
        filters={
            "type": "api_doc",
            "category": "reference"
        }
    )
```

## Task Management

### Recipe: Create and Track Tasks

```python
from mcp_codebase_insight.tasks.manager import TaskManager

async def manage_tasks(task_manager: TaskManager):
    # Create a new task
    task = await task_manager.create_task(
        title="Implement authentication",
        description="Add OAuth2 authentication to API endpoints",
        priority="high",
        tags=["security", "api"]
    )
    
    # Update task status
    await task_manager.update_task(
        task_id=task.id,
        status="in_progress",
        progress=0.5
    )
    
    # Query tasks
    active_tasks = await task_manager.get_tasks(
        filters={
            "status": "in_progress",
            "tags": ["security"]
        }
    )
```

## Transport Protocol Usage

### Recipe: Using SSE Transport

```python
from mcp_codebase_insight.transport.sse import SSETransport

async def setup_sse():
    transport = SSETransport(
        url="http://localhost:8000/events",
        headers={"Authorization": "Bearer your-token"}
    )
    
    async with transport:
        await transport.subscribe("codebase_updates")
        async for event in transport.events():
            print(f"Received update: {event.data}")
```

### Recipe: Using StdIO Transport

```python
from mcp_codebase_insight.transport.stdio import StdIOTransport

async def use_stdio():
    transport = StdIOTransport()
    
    async with transport:
        # Send command
        await transport.send_command({
            "type": "analyze",
            "payload": {"path": "src/main.py"}
        })
        
        # Receive response
        response = await transport.receive_response()
        print(f"Analysis result: {response}")
```

## Troubleshooting

### Recipe: Validate Vector Store Health

```python
async def check_vector_store_health(config: dict) -> bool:
    try:
        # Initialize components
        embedder = SentenceTransformerEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        await embedder.initialize()
        
        vector_store = VectorStore(
            url=config["QDRANT_URL"],
            embedder=embedder,
            collection_name=config["COLLECTION_NAME"]
        )
        await vector_store.initialize()
        
        # Test basic operations
        test_text = "def test_function():\n    pass"
        await vector_store.add_vector(
            text=test_text,
            metadata={"type": "test"}
        )
        
        results = await vector_store.search_similar(
            query=test_text,
            limit=1
        )
        
        return len(results) > 0
        
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
```

### Recipe: Debug Transport Issues

```python
import logging
from mcp_codebase_insight.transport.debug import TransportDebugger

async def debug_transport_issues():
    # Enable detailed logging
    logging.basicConfig(level=logging.DEBUG)
    
    debugger = TransportDebugger()
    
    # Test SSE connection
    sse_status = await debugger.check_sse_connection(
        url="http://localhost:8000/events"
    )
    print(f"SSE Status: {sse_status}")
    
    # Test StdIO communication
    stdio_status = await debugger.check_stdio_communication()
    print(f"StdIO Status: {stdio_status}")
    
    # Generate diagnostic report
    report = await debugger.generate_diagnostic_report()
    print(report)
```

## Best Practices

1. Always use async/await when working with the system's async functions
2. Initialize components in a context manager or properly handle cleanup
3. Use structured error handling for vector store operations
4. Implement retry logic for network-dependent operations
5. Cache frequently accessed vector embeddings
6. Use batch operations when processing multiple items
7. Implement proper logging for debugging
8. Regular health checks for system components

## Common Issues and Solutions

1. **Vector Store Connection Issues**
   - Check if Qdrant is running and accessible
   - Verify API key if authentication is enabled
   - Ensure proper network connectivity

2. **Embedding Generation Failures**
   - Verify model availability and access
   - Check input text formatting
   - Monitor memory usage for large inputs

3. **Transport Protocol Errors**
   - Verify endpoint URLs and authentication
   - Check for firewall or proxy issues
   - Monitor connection timeouts

4. **Performance Issues**
   - Use batch operations for multiple items
   - Implement caching where appropriate
   - Monitor and optimize vector store queries

For more detailed information, refer to the [official documentation](docs/README.md) and [API reference](docs/api-reference.md). 