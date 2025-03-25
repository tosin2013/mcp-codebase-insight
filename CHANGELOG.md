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
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

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
