# Development commands
.PHONY: install install-dev start stop clean test lint format check docs build publish publish-test version-patch version-minor version-major

# Default Python interpreter
PYTHON := python3.11
VENV := .venv

# Server settings
HOST := 127.0.0.1
PORT := 3000
LOG_LEVEL := INFO

# Install base dependencies
install:
	@echo "Installing dependencies..."
	@$(PYTHON) -m venv $(VENV)
	@. $(VENV)/bin/activate && pip install -e .

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	@$(PYTHON) -m venv $(VENV)
	@. $(VENV)/bin/activate && pip install -e ".[dev]"

# Ensure virtual environment
ensure_venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Please run 'make install' first."; \
		exit 1; \
	fi

# Start server
start: ensure_venv
	@echo "Starting MCP server..."
	@. $(VENV)/bin/activate && ./scripts/start_mcp_server.sh \
		--host $(HOST) \
		--port $(PORT) \
		--log-level $(LOG_LEVEL)

# Stop server
stop: ensure_venv
	@echo "Stopping MCP server..."
	@pkill -f "python -m src.mcp_server_qdrant" || true

# Clean build artifacts and caches
clean: ensure_venv
	@echo "Cleaning project..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".DS_Store" -delete
	@find . -type f -name "*.cache" -delete

# Build package
build: clean
	@echo "Building package..."
	@. $(VENV)/bin/activate && python -m build

# Publish to TestPyPI
publish-test: build
	@echo "Publishing to TestPyPI..."
	@. $(VENV)/bin/activate && twine upload --repository testpypi dist/*

# Publish to PyPI
publish: build
	@echo "Publishing to PyPI..."
	@. $(VENV)/bin/activate && twine upload dist/*

# Version management
version-patch:
	@echo "Bumping patch version..."
	@. $(VENV)/bin/activate && bump2version patch

version-minor:
	@echo "Bumping minor version..."
	@. $(VENV)/bin/activate && bump2version minor

version-major:
	@echo "Bumping major version..."
	@. $(VENV)/bin/activate && bump2version major

# Run tests
test: ensure_venv
	@echo "Running tests..."
	@. $(VENV)/bin/activate && pytest tests/ \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html \
		-v

# Run linting
lint: ensure_venv
	@echo "Running linters..."
	@. $(VENV)/bin/activate && ruff check src/ tests/
	@. $(VENV)/bin/activate && mypy src/ tests/

# Format code
format: ensure_venv
	@echo "Formatting code..."
	@. $(VENV)/bin/activate && black src/ tests/
	@. $(VENV)/bin/activate && isort src/ tests/

# Run all checks
check: format lint test
	@echo "All checks passed!"

# Load example patterns
load-patterns: ensure_venv
	@echo "Loading example patterns..."
	@. $(VENV)/bin/activate && python scripts/load_example_patterns.py

# Run example
example: ensure_venv
	@echo "Running example..."
	@. $(VENV)/bin/activate && python examples/use_with_claude.py

# Setup development environment
setup-dev: install-dev
	@echo "Setting up development environment..."
	@./scripts/macos_install.sh
	@make load-patterns

# Create new ADR
adr: ensure_venv
	@echo "Creating new ADR..."
	@. $(VENV)/bin/activate && python -m src.mcp_server_qdrant.tools.create_adr

# Update dependencies
update-deps: ensure_venv
	@echo "Updating dependencies..."
	@. $(VENV)/bin/activate && pip install --upgrade pip
	@. $(VENV)/bin/activate && pip install --upgrade -e ".[dev]"

# Show help
help:
	@echo "Available commands:"
	@echo "  make install      - Install base dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make start        - Start MCP server"
	@echo "  make stop         - Stop MCP server"
	@echo "  make clean        - Clean build artifacts and caches"
	@echo "  make test         - Run tests with coverage"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code"
	@echo "  make check        - Run all checks (format, lint, test)"
	@echo "  make load-patterns- Load example patterns"
	@echo "  make example      - Run example script"
	@echo "  make setup-dev    - Setup development environment"
	@echo "  make adr          - Create new ADR"
	@echo "  make update-deps  - Update dependencies"
	@echo "  make build        - Build package"
	@echo "  make publish-test - Publish to TestPyPI"
	@echo "  make publish      - Publish to PyPI"
	@echo "  make version-patch- Bump patch version"
	@echo "  make version-minor- Bump minor version"
	@echo "  make version-major- Bump major version"
	@echo "  make help         - Show this help message"

# Default target
.DEFAULT_GOAL := help
