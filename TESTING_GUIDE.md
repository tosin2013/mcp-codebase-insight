# Testing Guide for MCP Codebase Insight

**Version**: 0.3.0  
**Last Updated**: November 19, 2025

## Quick Start

### Prerequisites

```bash
# Python 3.10, 3.11, 3.12, or 3.13
python --version

# Qdrant vector database (for integration tests)
docker run -p 6333:6333 qdrant/qdrant:v1.13.6
```

### Installation

```bash
# Clone the repository
git clone https://github.com/tosin2013/mcp-codebase-insight.git
cd mcp-codebase-insight

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Running Tests

### Using Custom Test Runner (Recommended)

The project uses a custom test runner (`run_tests.py`) that handles async event loop isolation.

```bash
# Run all tests with isolation and coverage
./run_tests.py --all --isolated --coverage

# Run specific test categories
./run_tests.py --component --isolated      # Component tests
./run_tests.py --integration --isolated    # Integration tests
./run_tests.py --api --isolated            # API endpoint tests

# Run specific test file
./run_tests.py --file tests/components/test_cache.py

# Run specific test function
./run_tests.py --test test_vector_store_initialization
```

### Using pytest Directly (Not Recommended)

If you must use pytest directly:

```bash
# Basic test run
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Specific test file
python -m pytest tests/components/test_core_components.py -v

# With async mode
python -m pytest tests/ --asyncio-mode=strict
```

**Note**: Direct pytest usage may encounter event loop conflicts. Use the custom runner for best results.

## Test Categories

### 1. Component Tests

Test individual components in isolation.

```bash
./run_tests.py --component --isolated
```

**Tests Include**:
- ADR Manager (`test_adr_manager`)
- Cache Manager (`test_cache_manager`)
- Knowledge Base (`test_knowledge_base`)
- Vector Store (`test_vector_store`)
- Embeddings (`test_embeddings`)
- Task Manager (`test_task_manager`)
- SSE Components (`test_sse_components`)
- STDIO Components (`test_stdio_components`)

**Expected Results**:
- 7/8 tests passing (cache_manager may be intermittent)
- No critical failures

### 2. Integration Tests

Test multi-component interactions.

```bash
./run_tests.py --integration --isolated
```

**Tests Include**:
- Server initialization
- API endpoints
- Communication integration
- End-to-end workflows

**Prerequisites**:
- Qdrant running on localhost:6333
- All dependencies installed

### 3. Configuration Tests

Test configuration and environment handling.

```bash
./run_tests.py --file tests/config/test_config_and_env.py
```

## Manual Testing

### 1. Server Startup

```bash
# Start the server
python -m mcp_codebase_insight

# Or use the server script
python server.py
```

**Verify**:
- Server starts without errors
- No deprecation warnings
- Logs show proper initialization

### 2. API Endpoints

With server running, test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status": "healthy"}

# API documentation
curl http://localhost:8000/docs

# Should return OpenAPI documentation
```

### 3. Vector Search

```python
# test_vector_search.py
import asyncio
from src.mcp_codebase_insight.core.vector_store import VectorStore
from src.mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding

async def test_search():
    embedder = SentenceTransformerEmbedding()
    await embedder.initialize()
    
    store = VectorStore(embedder=embedder, collection_name="test")
    await store.initialize()
    
    # Add a test pattern
    await store.add_pattern(
        pattern_id="test1",
        code="def hello(): return 'world'",
        metadata={"type": "function"}
    )
    
    # Search
    results = await store.search("hello world function", limit=1)
    print(f"Found {len(results)} results")
    
    await store.cleanup()

asyncio.run(test_search())
```

### 4. Cache Operations

```python
# test_cache.py
import asyncio
from src.mcp_codebase_insight.core.cache import CacheManager

async def test_cache():
    cache = CacheManager(cache_enabled=True)
    await cache.initialize()
    
    # Set a value
    await cache.set("test_key", {"data": "test_value"})
    
    # Get the value
    result = await cache.get("test_key")
    print(f"Cache result: {result}")
    
    await cache.cleanup()

asyncio.run(test_cache())
```

## Performance Testing

### Basic Performance Metrics

```bash
# Time test execution
time ./run_tests.py --component --isolated

# Expected: < 2 minutes for component tests
```

### Load Testing (Manual)

```python
# load_test.py
import asyncio
import time
from src.mcp_codebase_insight.core.vector_store import VectorStore

async def load_test():
    store = VectorStore()
    await store.initialize()
    
    # Add 100 patterns
    start = time.time()
    for i in range(100):
        await store.add_pattern(
            pattern_id=f"pattern_{i}",
            code=f"def func_{i}(): pass",
            metadata={"index": i}
        )
    end = time.time()
    
    print(f"Added 100 patterns in {end-start:.2f} seconds")
    
    # Search performance
    start = time.time()
    for i in range(10):
        await store.search("function", limit=10)
    end = time.time()
    
    print(f"10 searches in {end-start:.2f} seconds")

asyncio.run(load_test())
```

## Security Testing

### 1. Dependency Vulnerability Scan

```bash
# Install pip-audit if not already installed
pip install pip-audit

# Run vulnerability scan
pip-audit

# Expected: 10 or fewer low-risk vulnerabilities (system packages)
```

### 2. Static Code Analysis

```bash
# Install bandit if not already installed
pip install bandit

# Run security scan
bandit -r src/ -f json -o bandit-report.json

# View results
cat bandit-report.json | python -m json.tool
```

**Expected Results**:
- 0 high-severity issues
- 0 medium-severity issues
- 2 or fewer low-severity issues (acceptable)

### 3. CodeQL Analysis

If running in CI/CD with CodeQL enabled:

```bash
# CodeQL is run automatically in GitHub Actions
# Check the Security tab in GitHub for results
```

## Platform-Specific Testing

### Linux (Ubuntu)

```bash
# Standard installation
sudo apt-get update
python3 --version
pip3 install -r requirements.txt
./run_tests.py --all --isolated
```

### macOS

```bash
# Using homebrew Python
brew install python@3.12
pip3 install -r requirements.txt
./run_tests.py --all --isolated
```

### Windows

```powershell
# Using Python from python.org
python --version
pip install -r requirements.txt
python run_tests.py --all --isolated
```

## Docker Testing

### Build and Test in Container

```bash
# Build the image
docker build -t mcp-codebase-insight .

# Run tests in container
docker run --rm mcp-codebase-insight pytest tests/

# Run with Qdrant
docker-compose up -d
docker-compose run app pytest tests/
```

## CI/CD Testing

Tests are automatically run in GitHub Actions on:
- Push to main/dev branches
- Pull requests
- Manual workflow dispatch

### Viewing CI Results

1. Go to GitHub Actions tab
2. Select the workflow run
3. View test results and coverage reports
4. Download artifacts if needed

## Troubleshooting

### Event Loop Errors

```
RuntimeError: There is no current event loop
```

**Solution**: Use the custom test runner with `--isolated` flag

```bash
./run_tests.py --component --isolated
```

### Qdrant Connection Errors

```
ConnectionError: Cannot connect to Qdrant
```

**Solution**: Ensure Qdrant is running

```bash
docker run -p 6333:6333 qdrant/qdrant:v1.13.6
```

### Import Errors

```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Solution**: Reinstall dependencies

```bash
pip install -r requirements.txt
```

### Memory Issues

```
RuntimeError: [enforce fail at alloc_cpu.cpp:...]
```

**Solution**: This usually indicates PyTorch needs more memory. Try:
- Closing other applications
- Using a smaller embedding model
- Increasing Docker memory limits (if using Docker)

## Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Core | 60% | 29% |
| API | 50% | ~40% |
| Utils | 70% | 79% |
| Overall | 50% | 29% |

**Note**: Coverage is improving with each release.

## Test Data

### Sample Code Patterns

```python
# Good examples for testing
patterns = [
    "def hello(): return 'world'",
    "class MyClass: pass",
    "async def fetch(): return await get_data()",
    "import os\nimport sys\n"
]
```

### Sample Metadata

```python
metadata = {
    "type": "function",
    "language": "python",
    "complexity": "low",
    "tags": ["utility", "helper"]
}
```

## Reporting Issues

If tests fail:

1. Capture the full error output
2. Note your environment (OS, Python version)
3. Include steps to reproduce
4. Check if it's a known issue (see RELEASE_NOTES.md)
5. Open an issue on GitHub

## Best Practices

1. **Always use isolated mode** for async tests
2. **Run security scans** before committing
3. **Check coverage** after adding new features
4. **Test on your target platform** before deployment
5. **Keep dependencies updated** monthly

## Additional Resources

- **Test Documentation**: `tests/README.test.md`
- **API Documentation**: `/docs` endpoint when server running
- **Architecture**: `system-architecture.md`
- **Contributing**: `CONTRIBUTING.md`

---

**Happy Testing!** 🧪

For questions or issues, please open an issue on GitHub.
