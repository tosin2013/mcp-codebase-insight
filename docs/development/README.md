# Development Guide

> 🚧 **Documentation In Progress**
> 
> This documentation is being actively developed. More details will be added soon.

## Overview

This guide covers development setup, contribution guidelines, and best practices for the MCP Codebase Insight project.

## Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/modelcontextprotocol/mcp-codebase-insight
   cd mcp-codebase-insight
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Setup Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Project Structure

```
mcp-codebase-insight/
├── src/
│   └── mcp_codebase_insight/
│       ├── analysis/       # Code analysis modules
│       ├── documentation/  # Documentation management
│       ├── kb/            # Knowledge base operations
│       └── server/        # FastAPI server
├── tests/
│   ├── integration/       # Integration tests
│   └── unit/             # Unit tests
├── docs/                 # Documentation
└── examples/            # Example usage
```

## Testing

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run with coverage
pytest --cov=src tests/
```

## Code Style

- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions focused and small
- Write tests for new features

## Git Workflow

1. Create feature branch
2. Make changes
3. Run tests
4. Submit pull request

## Documentation

- Update docs for new features
- Include docstrings
- Add examples when relevant

## Debugging

### Server Debugging
```python
import debugpy

debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

### VSCode Launch Configuration
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "port": 5678,
      "host": "localhost"
    }
  ]
}
```

## Performance Profiling

```bash
python -m cProfile -o profile.stats your_script.py
python -m snakeviz profile.stats
```

## Next Steps

- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [API Reference](../api/rest-api.md) 