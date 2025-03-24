# Test Structure

This directory contains the test suite for the MCP Codebase Insight project. The tests are organized into the following structure:

## Directory Structure

```
tests/
├── components/           # Component-level tests
│   ├── test_vector_store.py
│   ├── test_knowledge_base.py
│   ├── test_task_manager.py
│   └── ...
├── integration/         # Integration and API tests
│   ├── test_api_endpoints.py
│   └── test_server.py
├── config/             # Configuration tests
│   └── test_config_and_env.py
├── conftest.py         # Shared test fixtures
└── README.md           # This file
```

## Test Categories

1. **Component Tests** (`components/`)
   - Unit tests for individual components
   - Tests component initialization, methods, and cleanup
   - Isolated from other components where possible

2. **Integration Tests** (`integration/`)
   - Tests for API endpoints
   - Server lifecycle tests
   - Component interaction tests

3. **Configuration Tests** (`config/`)
   - Environment variable handling
   - Configuration file parsing
   - Directory setup and permissions

## API Test Coverage

The following API endpoints are tested in the integration tests:

| Endpoint | Test Status | Test File |
|----------|-------------|-----------|
| `/health` | ✅ Tested | `test_api_endpoints.py` |
| `/api/vector-store/search` | ✅ Tested | `test_api_endpoints.py` |
| `/api/docs/adrs` | ✅ Tested | `test_api_endpoints.py` |
| `/api/docs/adrs/{adr_id}` | ✅ Tested | `test_api_endpoints.py` |
| `/api/docs/patterns` | ✅ Tested | `test_api_endpoints.py` |
| `/api/docs/patterns/{pattern_id}` | ✅ Tested | `test_api_endpoints.py` |
| `/api/analyze` | ✅ Tested | `test_api_endpoints.py` |
| `/api/tasks/create` | ✅ Tested | `test_api_endpoints.py` |
| `/api/tasks` | ✅ Tested | `test_api_endpoints.py` |
| `/api/tasks/{task_id}` | ✅ Tested | `test_api_endpoints.py` |
| `/api/debug/issues` | ✅ Tested | `test_api_endpoints.py` |
| `/api/debug/issues/{issue_id}` | ✅ Tested | `test_api_endpoints.py` |
| `/api/debug/issues/{issue_id}/analyze` | ✅ Tested | `test_api_endpoints.py` |
| `/tools/*` | ✅ Tested | `test_api_endpoints.py` |

Each test verifies:
- Successful responses with valid input
- Error handling with invalid input
- Response structure and content validation
- Edge cases where applicable

## Running Tests

To run all tests:
```bash
python -m pytest tests/
```

To run specific test categories:
```bash
# Run component tests
python -m pytest tests/components/

# Run integration tests
python -m pytest tests/integration/

# Run config tests
python -m pytest tests/config/

# Run API endpoint tests only
python -m pytest tests/integration/test_api_endpoints.py

# Run tests for a specific API endpoint
python -m pytest tests/integration/test_api_endpoints.py::test_health_check
```

## Test Fixtures

Shared test fixtures are defined in `conftest.py` and include:

- `temp_dir`: Temporary directory for test files
- `test_config`: Server configuration for testing
- `embedder`: Sentence transformer embedder
- `vector_store`: Vector store instance
- `test_server`: Server instance for testing
- `test_client`: FastAPI test client
- `test_code`: Sample code for testing
- `test_adr`: Sample ADR data
- `env_vars`: Environment variables for testing

## Writing New Tests

1. Place new tests in the appropriate directory based on what they're testing
2. Use the shared fixtures from `conftest.py`
3. Follow the existing patterns for async tests and cleanup
4. Add proper docstrings and comments
5. Ensure proper cleanup in fixtures that create resources

## Test Dependencies

The test suite has the following dependencies:
- pytest
- pytest-asyncio
- httpx
- fastapi
- sentence-transformers

Make sure these are installed before running tests. 