# Testing Guide for MCP Codebase Insight

## Asynchronous Testing

The MCP Codebase Insight project uses asynchronous APIs and should be tested using proper async test clients. Here are guidelines for testing:

### Async vs Sync Testing Clients

The project provides two test client fixtures:

1. **`test_client`** - Use for asynchronous tests
   - Returns an `AsyncClient` from httpx
   - Must be used with `await` for requests
   - Must be used with `@pytest.mark.asyncio` decorator

2. **`sync_test_client`** - Use for synchronous tests
   - Returns a `TestClient` from FastAPI
   - Used for simpler tests where async is not needed
   - No need for await or asyncio decorators

### Example: Async Test

```python
import pytest

@pytest.mark.asyncio
async def test_my_endpoint(test_client):
    """Test an endpoint asynchronously."""
    response = await test_client.get("/my-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
```

### Example: Sync Test

```python
def test_simple_endpoint(sync_test_client):
    """Test an endpoint synchronously."""
    response = sync_test_client.get("/simple-endpoint")
    assert response.status_code == 200
```

### Common Issues

1. **Using TestClient with async:** The error `'TestClient' object does not support the asynchronous context manager protocol` occurs when trying to use TestClient in an async context. Always use the `test_client` fixture for async tests.

2. **Mixing async/sync:** Don't mix async and sync patterns in the same test.

3. **Missing asyncio mark:** Always add `@pytest.mark.asyncio` to async test functions.

## Test Isolation

Tests should be isolated to prevent state interference between tests:

1. Each test gets its own server instance with isolated state
2. Vector store tests use unique collection names
3. Cleanup is performed automatically after tests

## Running Tests

Run tests using pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file_relationships.py

# Run specific test function
pytest tests/test_file_relationships.py::test_create_file_relationship
```

For more advanced test running options, use the `run_tests.py` script in the project root. 