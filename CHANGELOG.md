# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup
- Core server implementation
- ADR management system
- Documentation management
- Knowledge base with vector search
- Debug system
- Task management
- Metrics and health monitoring
- Caching system
- Structured logging
- Docker support
- CI/CD pipeline
- Test suite

### Changed
- Updated `aiohttp` from 3.11.14 (yanked) to 3.13.2
- Updated `fastapi` from 0.115.12 to 0.121.2
- Updated `starlette` from 0.46.1 to 0.49.3
- Updated `mcp` from 1.6.0 to 1.21.2
- Updated `transformers` from 4.50.3 to 4.57.1
- Updated `urllib3` from 2.3.0 to 2.5.0
- Updated `h11` from 0.14.0 to 0.16.0
- Updated `h2` from 4.2.0 to 4.3.0
- Updated `requests` from 2.32.3 to 2.32.4
- Updated `setuptools` from 78.1.0 to 78.1.1
- Migrated from deprecated `datetime.utcnow()` to `datetime.now(timezone.utc)` (42 occurrences)
- Improved async event loop handling in tests and core components

### Deprecated
- None

### Removed
- Removed yanked dependency version aiohttp 3.11.14
- Removed fsspec yanked version constraint

### Fixed
- Fixed 4 ReDoS vulnerabilities in transformers library (GHSA-9356-575x-2w9m, GHSA-59p9-h35m-wg4g, GHSA-rcv9-qm8p-9p6j, GHSA-4w7r-h757-3r74)
- Fixed 2 SSRF vulnerabilities in urllib3 (GHSA-48p4-8xcf-vxj5, GHSA-pq67-6m6q-mj2v)
- Fixed XSS vulnerabilities in starlette (GHSA-2c2j-9gv5-cj73, GHSA-7f5h-v6xp-fcq8)
- Fixed security issues in mcp library (GHSA-3qhf-m339-9g5v, GHSA-j975-95f5-7wqh)
- Fixed deprecation warnings for datetime.utcnow() usage across codebase
- Fixed deprecation warnings for asyncio.get_event_loop() in tests
- Improved test reliability and event loop handling

### Security
- **Critical**: Fixed 10+ known security vulnerabilities through dependency updates
- Completed security audit with bandit (only 2 low-severity issues remain)
- Reduced pip-audit vulnerabilities from 20 to 10 (remaining are system packages)
- Updated all security-critical dependencies to latest stable versions

## [0.2.2] - 2025-03-25

### Added
- Implemented single source of truth for versioning

### Changed
- Moved version to the package's __init__.py file as the canonical source
- Updated setup.py to dynamically read version from __init__.py
- Updated pyproject.toml to use dynamic versioning
- Synchronized dependencies between setup.py, pyproject.toml and requirements.in

### Fixed
- Missing dependencies in setup.py and pyproject.toml

## [0.2.1] - 2025-03-25

### Added
- Integrated Qdrant Docker container in CI/CD workflow for more realistic testing
- Added collection initialization step for proper Qdrant setup in CI/CD
- Created shared Qdrant client fixture for improved test reliability

### Changed
- Updated Python version requirement from >=3.11 to >=3.9 for broader compatibility
- Enhanced test fixture scoping to resolve event_loop fixture scope mismatches
- Improved connection verification for Qdrant in GitHub Actions workflow

### Fixed
- Resolved fixture scope mismatches in async tests
- Fixed environment variable handling in test configuration

### Removed
- None

### Security
- None

## [0.2.0] - 2025-03-24

### Added
- None

### Changed
- Improved async test fixture handling in component tests
- Enhanced test discovery to properly distinguish between test functions and fixtures
- Updated component test runner for better isolation and resource management

### Fixed
- Resolved fixture scope mismatches in async tests
- Fixed async event loop handling in component tests
- Corrected test_metadata fixture identification in test_vector_store.py

### Removed
- None

### Security
- None

## [0.1.0] - 2025-03-19

### Added
- Initial release
- Basic server functionality
- Core components:
  - ADR management
  - Documentation handling
  - Knowledge base
  - Vector search
  - Task management
  - Health monitoring
  - Metrics collection
  - Caching
  - Logging
- Docker support
- CI/CD pipeline with GitHub Actions
- Test coverage with pytest
- Code quality tools:
  - Black
  - isort
  - flake8
  - mypy
- Documentation:
  - README
  - API documentation
  - Contributing guidelines
  - ADR templates
- Development tools:
  - Makefile
  - Docker compose
  - Environment configuration
  - Version management

[Unreleased]: https://github.com/modelcontextprotocol/mcp-codebase-insight/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/modelcontextprotocol/mcp-codebase-insight/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/modelcontextprotocol/mcp-codebase-insight/releases/tag/v0.2.1
[0.2.0]: https://github.com/modelcontextprotocol/mcp-codebase-insight/releases/tag/v0.2.0
[0.1.0]: https://github.com/modelcontextprotocol/mcp-codebase-insight/releases/tag/v0.1.0
