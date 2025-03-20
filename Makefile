.PHONY: help install test lint format clean build run docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linters"
	@echo "  make format       Format code"
	@echo "  make clean        Clean build artifacts"
	@echo "  make build        Build package"
	@echo "  make run          Run server"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container"

# Install dependencies
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests \
		--cov=src \
		--cov-report=html \
		--cov-report=term \
		-v

# Run linters
lint:
	python -m flake8 src tests
	python -m mypy src tests
	python -m black --check src tests
	python -m isort --check-only src tests

# Format code
format:
	python -m black src tests
	python -m isort src tests

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Build package
build: clean
	python -m pip install --upgrade build
	python -m build

# Run server
run:
	python -m mcp_codebase_insight

# Docker commands
docker-build:
	docker build -t mcp-codebase-insight .

docker-run:
	docker run -p 3000:3000 \
		--env-file .env \
		-v $(PWD)/docs:/app/docs \
		-v $(PWD)/knowledge:/app/knowledge \
		-v $(PWD)/cache:/app/cache \
		-v $(PWD)/logs:/app/logs \
		mcp-codebase-insight

# Development environment setup
dev-setup: install
	pre-commit install
	pip install -e .

# Run style checks
style: lint format

# Run all checks
check: style test

# Create directories
init:
	mkdir -p docs/adrs knowledge cache logs

# Update dependencies
update-deps:
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

# Generate documentation
docs:
	pdoc --html --output-dir docs/api src/mcp_codebase_insight

# Version management
bump-patch:
	bump2version patch

bump-minor:
	bump2version minor

bump-major:
	bump2version major
