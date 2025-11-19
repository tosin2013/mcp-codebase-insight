# MCP Codebase Insight - AI Agent Instructions

## Architecture Overview

**MCP Server with Vector-Backed Knowledge Base**: FastAPI-based Model Context Protocol server providing codebase analysis through Qdrant vector store, semantic search with `sentence-transformers`, and pattern detection.

### Core Service Components (`src/mcp_codebase_insight/core/`)
- **VectorStore** (`vector_store.py`): Qdrant client wrapper with retry logic, collection initialization
- **EmbeddingProvider** (`embeddings.py`): Sentence transformers (`all-MiniLM-L6-v2` default), lazy initialization
- **CacheManager** (`cache.py`): Dual-layer (memory + disk) caching for embeddings and API results
- **KnowledgeBase** (`knowledge.py`): Semantic search over stored patterns with vector similarity
- **ServerState** (`state.py`): Component lifecycle via DIContainer, async initialization/cleanup tracking
- **ADRManager** (`adr.py`): Markdown frontmatter-based Architecture Decision Records in `docs/adrs/`

### Service Initialization Pattern
All core services follow async init/cleanup: `await service.initialize()` → use service → `await service.cleanup()`. ServerState manages component lifecycle through DIContainer, tracking status with `ComponentStatus` enum. See `server_lifespan()` in `server.py` for orchestration example.

### Configuration & Environment
- **ServerConfig** (`core/config.py`): Uses `@dataclass`, loads from env with `ServerConfig.from_env()`
- **Key env vars**: `QDRANT_URL`, `MCP_EMBEDDING_MODEL`, `MCP_COLLECTION_NAME`, `MCP_CACHE_ENABLED`, `MCP_DISK_CACHE_DIR`
- **Directory structure**: Config auto-creates `docs/`, `docs/adrs/`, `knowledge/`, `cache/` on init via `config.create_directories()`

## Development Workflows

### Running Tests
**Custom test runner**: `./run_tests.py` (NOT plain pytest) - handles asyncio isolation, event loop cleanup
```bash
# Run all tests with isolation and coverage
./run_tests.py --all --clean --isolated --coverage

# Run specific test categories
./run_tests.py --component --isolated      # Component tests
./run_tests.py --integration --isolated    # Integration tests
./run_tests.py --api --isolated            # API endpoint tests

# Run specific test file or function
./run_tests.py --file tests/components/test_cache.py
./run_tests.py --test test_vector_store_initialization
```

**Why custom runner?**: Event loop conflicts between test modules. Runner provides `--isolated` (PYTHONPATH isolation), `--sequential` (no parallelism), `--fully-isolated` (separate processes per module).

### Makefile Commands
```bash
make install      # Install dependencies from requirements.txt
make test         # Runs ./run_tests.py with recommended flags
make lint         # flake8 + mypy + black --check + isort --check
make format       # black + isort code formatting
make run          # python -m mcp_codebase_insight
make docker-build # Build container with Qdrant integration
```

### Docker & Qdrant Setup
- **Dockerfile**: Python 3.11-slim, Rust toolchain (pydantic build), multi-stage cache optimization
- **Qdrant**: External vector DB (port 6333), not bundled. Start via `docker-compose` or local install
- **Container mounts**: Mount `docs/`, `knowledge/`, `cache/`, `logs/` for persistence

## Code Conventions & Patterns

### Async/Await Discipline
- **All I/O operations are async**: File system via `aiofiles`, Qdrant via async client, cache operations
- **Test isolation**: `conftest.py` manages session-scoped event loops with `_event_loops` dict, mutex locks (`_loops_lock`, `_tests_lock`)
- **Fixtures**: Use `@pytest_asyncio.fixture` for async fixtures, `@pytest.mark.asyncio` for async tests

### Error Handling & Logging
- **Structured logging**: `from ..utils.logger import get_logger` → `logger = get_logger(__name__)`
- **Component-level error tracking**: ServerState stores errors in ComponentState, retry counts tracked
- **Graceful degradation**: VectorStore initialization can fail (Qdrant unavailable), server continues with reduced functionality

### Testing Patterns
- **Test fixtures in conftest.py**: `event_loop`, `test_config`, `vector_store`, `cache_manager` (session/function scoped)
- **Isolation via server_test_isolation.py**: `get_isolated_server_state()` provides per-test server instances
- **Component tests**: Focus on single service unit (e.g., `test_vector_store.py` → VectorStore CRUD operations)
- **Integration tests**: Multi-component workflows (e.g., `test_api_endpoints.py` → FastAPI routes with live services)

### Dependency Injection Pattern
DIContainer (`core/di.py`) manages component initialization order:
1. ServerConfig from env
2. Embedding model (SentenceTransformer)
3. VectorStore (needs embedder + Qdrant client)
4. CacheManager, MetricsManager, HealthManager
5. KnowledgeBase (needs VectorStore)
6. TaskManager, ADRManager

**Usage**: Create DIContainer, call `await container.initialize()`, access via `container.get_component("vector_store")`

### Type Hints & Dataclasses
- **Strict typing**: All functions have type hints (params + return types), mypy enforced in lint
- **@dataclass for config/models**: ServerConfig, ComponentState, ADR, SearchResult use dataclasses
- **Optional vs None**: Use `Optional[Type]` for potentially None values, explicit None checks

## Key File Relationships

- **server.py** → imports core services, defines `server_lifespan` context manager
- **core/state.py** → imports DIContainer, manages component registry
- **core/di.py** → imports all service classes, orchestrates initialization
- **tests/conftest.py** → imports ServerState, server_test_isolation for fixture setup
- **run_tests.py** → spawns pytest subprocess with custom args, handles event loop cleanup

## Project-Specific Quirks

1. **Qdrant client version sensitivity**: Comments in `vector_store.py` note parameter name changes (`query_vector` → `query` in v1.13.3+). Code supports both for compatibility.

2. **Cache directory creation**: `disk_cache_dir` defaults to `"cache"` if `MCP_CACHE_ENABLED=true` but path not specified. Set to `None` if cache disabled (see `ServerConfig.__post_init__`).

3. **ADR numbering**: ADRManager auto-increments `next_adr_number` by scanning `docs/adrs/` for `NNN-*.md` patterns on init.

4. **Test runner event loop management**: `conftest.py` maintains process-specific event loop dict to avoid "different loop" errors across test modules.

5. **Component status tracking**: Don't assume component is ready after creation. Check `component.status == ComponentStatus.INITIALIZED` before use.

## Common Debugging Patterns

- **Qdrant connection issues**: Check `QDRANT_URL` env var, verify Qdrant is running (`curl http://localhost:6333/collections`)
- **Event loop errors in tests**: Use `--isolated` and `--sequential` flags with `run_tests.py`, check `conftest.py` fixtures are async
- **Missing embeddings**: EmbeddingProvider lazy-loads model on first use, check `initialized` flag
- **Cache not persisting**: Verify `MCP_DISK_CACHE_DIR` is writable, check `cache_enabled` in config

## References

- **System architecture diagrams**: `system-architecture.md` (Mermaid diagrams for components, data flow)
- **Detailed setup guides**: `docs/getting-started/` for installation, Qdrant setup, Docker
- **Testing philosophy**: Follows TDD, see `docs/tdd/workflow.md` and Agans' 9 Rules in `docs/debuggers/`
- **Existing AI context**: `CLAUDE.md` has legacy build/test commands (superseded by Makefile + run_tests.py)
