# Development Guide

> 🚧 **Documentation In Progress**
> 
> This documentation is being actively developed. More details will be added soon.

## Overview

This document provides guidance for developers working on the MCP Codebase Insight project. For workflow information, please see the [Workflows Documentation](../workflows/README.md).

## Getting Started

### Prerequisites
- Python 3.11 or higher
- pip
- Git
- Docker (optional)

### Development Setup
1. Clone the repository
   ```bash
   git clone https://github.com/modelcontextprotocol/mcp-codebase-insight.git
   cd mcp-codebase-insight
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

### Running Tests
```bash
pytest tests/
```

## Project Structure

```
mcp-codebase-insight/
├── docs/                 # Documentation
├── src/                 # Source code
│   └── mcp_codebase_insight/
│       ├── core/        # Core functionality
│       ├── utils/       # Utilities
│       └── server.py    # Main server
├── tests/              # Test suite
├── scripts/            # Development scripts
└── requirements.txt    # Dependencies
```

## Development Workflow

1. Create a new branch
2. Make changes
3. Run tests
4. Submit pull request

See the [Contributing Guide](../../CONTRIBUTING.md) for more details. 