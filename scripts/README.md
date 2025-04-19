# Utility Scripts

This directory contains utility scripts for the MCP Codebase Insight project.

## Available Scripts

### check_qdrant_health.sh

**Purpose**: Checks if the Qdrant vector database service is available and healthy.

**Usage**:
```bash
./check_qdrant_health.sh [qdrant_url] [max_retries] [sleep_seconds]
```

**Parameters**:
- `qdrant_url` - URL of the Qdrant service (default: "http://localhost:6333")
- `max_retries` - Maximum number of retry attempts (default: 20)
- `sleep_seconds` - Seconds to wait between retries (default: 5)

**Example**:
```bash
./check_qdrant_health.sh "http://localhost:6333" 30 2
```

> Note: This script uses `apt-get` and may require `sudo` privileges on Linux systems. Ensure `curl` and `jq` are pre-installed or run with proper permissions.

**Exit Codes**:
- 0: Qdrant service is accessible and healthy
- 1: Qdrant service is not accessible or not healthy

### compile_requirements.sh

**Purpose**: Compiles and generates version-specific requirements files for different Python versions.

**Usage**:
```bash
./compile_requirements.sh <python-version>
```

**Example**:
```bash
./compile_requirements.sh 3.11
```

### load_example_patterns.py

**Purpose**: Loads example patterns and ADRs into the knowledge base for demonstration or testing.

**Usage**:
```bash
python load_example_patterns.py [--help]
```

### verify_build.py

**Purpose**: Verifies the build status and generates a build verification report.

**Usage**:
```bash
python verify_build.py [--config <file>] [--output <report-file>]
```

## Usage in GitHub Actions

These scripts are used in our GitHub Actions workflows to automate and standardize common tasks. For example, `check_qdrant_health.sh` is used in both the build verification and TDD verification workflows to ensure the Qdrant service is available before running tests.

## Adding New Scripts

When adding new scripts to this directory:

1. Make them executable: `chmod +x scripts/your_script.sh`
2. Include a header comment explaining the purpose and usage
3. Add error handling and sensible defaults
4. Update this README with information about the script
5. Use parameter validation and help text when appropriate 