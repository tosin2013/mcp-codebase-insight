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
* Include screenshots and animated GIFs if possible

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the Python style guides
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Process

1. Fork the repo
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`make test`)
5. Run the linters (`make lint`)
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/mcp-codebase-insight.git
cd mcp-codebase-insight

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make dev-setup

# Run tests
make test

# Run linters
make lint

# Format code
make format
```

### Project Structure

```
mcp-codebase-insight/
├── docs/               # Documentation
├── src/               # Source code
│   └── mcp_codebase_insight/
│       ├── core/      # Core functionality
│       └── utils/     # Utilities
├── tests/             # Test suite
├── scripts/           # Utility scripts
└── examples/          # Example code
```

## Style Guides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Style Guide

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use [Black](https://black.readthedocs.io/) for code formatting
* Use [isort](https://pycqa.github.io/isort/) for import sorting
* Use [mypy](http://mypy-lang.org/) for type checking
* Use [flake8](https://flake8.pycqa.org/) for linting

### Documentation Style Guide

* Use [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings
* Keep docstrings clear and concise
* Include examples in docstrings when appropriate
* Document both the what and the why

## Additional Notes

### Issue and Pull Request Labels

* `bug`: Something isn't working
* `enhancement`: New feature or request
* `documentation`: Improvements or additions to documentation
* `good first issue`: Good for newcomers
* `help wanted`: Extra attention is needed
* `question`: Further information is requested

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
