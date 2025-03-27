# Contributing Guidelines

> 🚧 **Documentation In Progress**
> 
> This documentation is being actively developed. More details will be added soon.

## Welcome!

Thank you for considering contributing to MCP Codebase Insight! This document provides guidelines and workflows for contributing.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
2. If not, create a new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

### Suggesting Enhancements

1. Check existing issues and discussions
2. Create a new issue with:
   - Clear title
   - Detailed description
   - Use cases
   - Implementation ideas (optional)

### Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit PR with:
   - Clear title
   - Description of changes
   - Reference to related issues
   - Updated documentation

## Development Process

### 1. Setup Development Environment

Follow the [Development Guide](README.md) for setup instructions.

### 2. Make Changes

1. Create a branch:
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make changes following our style guide
3. Add tests for new functionality
4. Update documentation

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/path/to/test_file.py

# Run with coverage
pytest --cov=src tests/
```

### 4. Submit Changes

1. Push to your fork
2. Create pull request
3. Wait for review
4. Address feedback

## Style Guide

### Python Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use docstrings (Google style)

### Commit Messages

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

### Documentation

- Keep README.md updated
- Add docstrings to all public APIs
- Update relevant documentation files
- Include examples for new features

## Review Process

1. Automated checks must pass
2. At least one maintainer review
3. All feedback addressed
4. Documentation updated
5. Tests added/updated

## Getting Help

- Join our [Discord](https://discord.gg/mcp-codebase-insight)
- Ask in GitHub Discussions
- Contact maintainers

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 