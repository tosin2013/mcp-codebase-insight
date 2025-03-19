# Contributing to MCP Codebase Insight

First off, thank you for considering contributing to MCP Codebase Insight! It's people like you that make it such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include any error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide the following information:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python style guide
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Process

1. Fork the repo
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`make install-dev`)
4. Make your changes
5. Run tests and linting (`make check`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/mcp-codebase-insight.git
cd mcp-codebase-insight

# Install dependencies
make install-dev

# Start Qdrant container
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest

# Run tests
make test

# Format code
make format

# Run linting
make lint
```

### Testing

* Write tests for new features
* Run the test suite with `make test`
* Ensure coverage remains high
* Run tests with multiple Python versions locally if possible

### Documentation

* Update the README.md with details of changes to the interface
* Update the CHANGELOG.md following the Keep a Changelog format
* Add or update docstrings
* Comment complex code sections

## Release Process

1. Update CHANGELOG.md
2. Bump version (`make version-patch`, `make version-minor`, or `make version-major`)
3. Create GitHub release
4. CI/CD will automatically publish to PyPI

## Questions?

Feel free to open an issue with your question or contact the maintainers directly.
