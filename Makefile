.PHONY: help install install-uvx install-uvx-v2 test lint format clean build build-uvx run run-uvx run-uvx-v2 run-uvx-auto docker-build docker-run run-direct

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies using pip"
	@echo "  make install-uvx  Install dependencies using UVX v1"
	@echo "  make install-uvx-v2 Install dependencies using UVX v2"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linters"
	@echo "  make format       Format code"
	@echo "  make clean        Clean build artifacts"
	@echo "  make build        Build package using setuptools"
	@echo "  make build-uvx    Build package using UVX"
	@echo "  make run          Run server using Python"
	@echo "  make run-uvx      Run server using UVX v1"
	@echo "  make run-uvx-v2   Run server using UVX v2"
	@echo "  make run-uvx-auto Run server using UVX (auto-detects version)"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container"
	@echo "  make run-direct   Run server directly using Python module"

# Install dependencies
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

# Run tests
test:
	./run_tests.py --all --clean --isolated --coverage

# Run specific test categories
test-api:
	./run_tests.py --api --isolated

test-integration:
	./run_tests.py --integration --isolated

test-component:
	./run_tests.py --component --isolated

test-config:
	./run_tests.py --config --isolated

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

# Build package using UVX
build-uvx: clean
	python -m pip install --upgrade "uvx<2.0"
	uvx runpip install build
	uvx run python -m build

# Run server with Python
run:
	python -m mcp_codebase_insight.server --debug --port 3000

# Run server with UVX
run-uvx:
	python -m pip install --upgrade "uvx<2.0"
	uvx run python -m mcp_codebase_insight.server --debug --port 3000

# Run server with Docker
run-docker:
	docker build -t mcp-codebase-insight .
	docker run -p 3000:3000 mcp-codebase-insight

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

# Install dependencies using UVX
install-uvx:
	python -m pip install --upgrade pip
	python -m pip install --upgrade "uvx<2.0"
	uvx install .

# Install dependencies using UVX v2
install-uvx-v2:
	python -m pip install --upgrade pip
	python -m pip install uvx
	uvx install .

# Development environment setup
dev-setup: install
	pre-commit install
	pip install -e .

# Development environment setup with UVX
dev-setup-uvx: install-uvx
	uvx runpip install pre-commit
	pre-commit install

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

# Run server with UVX v2
run-uvx-v2:
	python -m pip install --upgrade uvx
	uvx install -e .
	uvx run uvicorn mcp_codebase_insight.server:app --host 127.0.0.1 --port 3000 --reload

# Run server with UVX (auto-detects version)
run-uvx-auto:
	@if command -v uvx >/dev/null 2>&1; then \
		if uvx --version | grep -q "2."; then \
			make run-uvx-v2; \
		else \
			make run-uvx; \
		fi \
	else \
		echo "UVX not found, running with Python"; \
		make run; \
	fi

# Run server directly using Python module
run-direct:
	python -m mcp_codebase_insight.server --debug --port 3000
