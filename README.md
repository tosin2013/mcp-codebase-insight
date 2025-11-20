# MCP Codebase Insight - WIP

> 🚧 **Development in Progress**
>
> This project is actively under development. Features and documentation are being continuously updated.

## Overview

MCP Codebase Insight is a system for analyzing and understanding codebases through semantic analysis, pattern detection, and documentation management.

## Current Development Status

### Completed Features
- ✅ Core Vector Store System
- ✅ Basic Knowledge Base
- ✅ SSE Integration
- ✅ Testing Framework
- ✅ TDD and Debugging Framework (rules_template integration)

### In Progress
- 🔄 Documentation Management System
- 🔄 Advanced Pattern Detection
- 🔄 Performance Optimization
- 🔄 Integration Testing
- 🔄 Debugging Utilities Enhancement

### Planned
- 📋 Extended API Documentation
- 📋 Custom Pattern Plugins
- 📋 Advanced Caching Strategies
- 📋 Deployment Guides
- 📋 Comprehensive Error Tracking System

## Quick Start

1. **Installation**

   **Recommended method (using UVX for Python 3.10+):**
   ```bash
   # Install UVX package manager
   pip install "uvx<2.0"

   # Install MCP Codebase Insight
   pip install mcp-codebase-insight

   # For development installation (from source)
   pip install -e .
   ```

   Alternative method (using pip directly):
   ```bash
   pip install mcp-codebase-insight
   ```

2. **Basic Usage**
   ```python
   from mcp_codebase_insight import CodebaseAnalyzer

   analyzer = CodebaseAnalyzer()
   results = analyzer.analyze_code("path/to/code")
   ```

3. **Running the Server**
   ```bash
   # Using the Makefile
   make run

   # Using the Makefile with UVX
   make run-uvx

   # Using Docker (most reliable method)
   make run-docker

   # Or using Python directly
   python -m mcp_codebase_insight.server --debug --port 3000

   # Note: The server currently has an issue with the --reload flag
   # This is a known issue with the server implementation
   ```

4. **Running Tests**
   ```bash
   # Run all tests
   pytest tests/

   # Run unit tests
   pytest tests/unit/

   # Run component tests
   pytest tests/components/

   # Run tests with coverage
   pytest tests/ --cov=src --cov-report=term-missing
   ```

5. **Debugging Utilities**
   ```python
   from mcp_codebase_insight.utils.debug_utils import debug_trace, DebugContext, get_error_tracker

   # Use debug trace decorator
   @debug_trace
   def my_function():
       # Implementation

   # Use debug context
   with DebugContext("operation_name"):
       # Code to debug

   # Track errors
   try:
       # Risky operation
   except Exception as e:
       error_id = get_error_tracker().record_error(e, context={"operation": "description"})
       print(f"Error recorded with ID: {error_id}")
   ```

## Testing and Debugging

### Test-Driven Development

This project follows Test-Driven Development (TDD) principles:

1. Write a failing test first (Red)
2. Write minimal code to make the test pass (Green)
3. Refactor for clean code while keeping tests passing (Refactor)

Our TDD documentation can be found in [docs/tdd/workflow.md](docs/tdd/workflow.md).

### Debugging Framework

We use Agans' 9 Rules of Debugging:

1. Understand the System
2. Make It Fail
3. Quit Thinking and Look
4. Divide and Conquer
5. Change One Thing at a Time
6. Keep an Audit Trail
7. Check the Plug
8. Get a Fresh View
9. If You Didn't Fix It, It Isn't Fixed

Learn more about our debugging approach in [docs/debuggers/agans_9_rules.md](docs/debuggers/agans_9_rules.md).

## Documentation

- [System Architecture](docs/system_architecture/README.md)
- [Core Components](docs/components/README.md)
- [API Reference](docs/api/README.md)
- [Development Guide](docs/development/README.md)
- [UVX Installation Guide](docs/getting-started/uvx_installation.md)
- [Workflows](docs/workflows/README.md)
- [TDD Workflow](docs/tdd/workflow.md)
- [Debugging Practices](docs/debuggers/best_practices.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issue Tracker](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
- [Discussions](https://github.com/modelcontextprotocol/mcp-codebase-insight/discussions)
