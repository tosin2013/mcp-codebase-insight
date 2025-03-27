# Code Analysis

MCP Codebase Insight provides powerful code analysis capabilities to help you understand patterns, identify issues, and improve code quality.

## Overview

The code analysis feature:
- Identifies common design patterns
- Detects potential issues and anti-patterns
- Suggests improvements and optimizations
- Analyzes code relationships and dependencies
- Provides semantic understanding of code

## Features

### 1. Pattern Detection

The system can identify common software design patterns:

```python
# Example: Factory Pattern Detection
class Creator:
    def factory_method(self):
        pass
    
    def some_operation(self):
        product = self.factory_method()
        result = product.operation()
        return result

class ConcreteCreator(Creator):
    def factory_method(self):
        return ConcreteProduct()
```

Analysis will identify this as a Factory Pattern implementation.

### 2. Code Quality Analysis

Identifies potential issues and suggests improvements:

- Code complexity metrics
- Duplicate code detection
- Dead code identification
- Resource management issues
- Error handling patterns

### 3. Dependency Analysis

Maps relationships between code components:

```python
# Example: Analyzing imports and dependencies
response = await client.post(
    "http://localhost:3000/api/analyze/dependencies",
    json={
        "file_path": "src/main.py",
        "depth": 2  # How deep to analyze dependencies
    }
)

dependencies = response.json()
```

### 4. Semantic Analysis

Understands code meaning and context:

```python
# Example: Semantic code search
response = await client.post(
    "http://localhost:3000/api/analyze/semantic",
    json={
        "query": "find all functions that handle user authentication",
        "scope": ["src/auth/", "src/users/"]
    }
)

matches = response.json()
```

## Usage

### Basic Analysis

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:3000/api/analyze",
        json={
            "code": your_code,
            "language": "python",
            "analysis_type": ["patterns", "quality", "dependencies"]
        }
    )
    
    results = response.json()
    print(results["patterns"])
    print(results["quality_issues"])
    print(results["dependencies"])
```

### Continuous Analysis

Set up continuous analysis in your CI/CD pipeline:

```bash
# Example: GitHub Actions workflow
curl -X POST http://localhost:3000/api/analyze/ci \
    -H "Content-Type: application/json" \
    -d '{
        "repository": "owner/repo",
        "branch": "main",
        "commit": "sha",
        "diff_only": true
    }'
```

### Batch Analysis

Analyze multiple files or entire directories:

```python
# Analyze entire directory
response = await client.post(
    "http://localhost:3000/api/analyze/batch",
    json={
        "path": "src/",
        "include": ["*.py", "*.js"],
        "exclude": ["*_test.py", "node_modules"],
        "analysis_type": ["patterns", "quality"]
    }
)
```

## Configuration

### Analysis Settings

```yaml
analysis:
  # Pattern detection settings
  patterns:
    confidence_threshold: 0.8
    min_pattern_size: 5
    
  # Quality analysis settings
  quality:
    max_complexity: 15
    max_line_length: 100
    enable_type_checking: true
    
  # Dependency analysis settings
  dependencies:
    max_depth: 3
    include_external: true
    
  # Semantic analysis settings
  semantic:
    model: "code-bert-base"
    similarity_threshold: 0.7
```

### Custom Rules

Create custom analysis rules:

```python
# Example: Custom pattern rule
{
    "name": "custom_singleton",
    "pattern": {
        "type": "class",
        "properties": {
            "has_private_constructor": true,
            "has_static_instance": true
        }
    },
    "message": "Possible Singleton pattern detected"
}
```

## Integration

### IDE Integration

The analysis features can be integrated with popular IDEs:

- VS Code Extension
- JetBrains Plugin
- Vim/Neovim Plugin

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Code Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run MCP Analysis
        run: |
          curl -X POST http://localhost:3000/api/analyze/ci \
            -H "Content-Type: application/json" \
            -d '{
              "repository": "${{ github.repository }}",
              "commit": "${{ github.sha }}",
              "diff_only": true
            }'
```

## Best Practices

1. **Regular Analysis**
   - Run analysis on every commit
   - Set up automated analysis in CI/CD
   - Review analysis results in code reviews

2. **Custom Rules**
   - Create project-specific rules
   - Maintain a rule catalog
   - Version control your rules

3. **Performance**
   - Use selective analysis for large codebases
   - Enable caching for repeated analysis
   - Configure appropriate thresholds

4. **Integration**
   - Integrate with your IDE
   - Add to your CI/CD pipeline
   - Connect with code review tools

## Troubleshooting

### Common Issues

1. **Analysis Timeout**
   ```yaml
   # Increase timeout in config
   analysis:
     timeout: 300  # seconds
   ```

2. **High Memory Usage**
   ```yaml
   # Adjust batch size
   analysis:
     batch_size: 50
   ```

3. **False Positives**
   ```yaml
   # Adjust confidence thresholds
   analysis:
     patterns:
       confidence_threshold: 0.9
   ```

## API Reference

### Analysis Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/analyze` | Basic code analysis |
| `/api/analyze/batch` | Batch analysis |
| `/api/analyze/ci` | CI/CD integration |
| `/api/analyze/dependencies` | Dependency analysis |
| `/api/analyze/semantic` | Semantic analysis |

### Response Format

```json
{
    "analysis_id": "uuid",
    "status": "completed",
    "results": {
        "patterns": [...],
        "quality": {...},
        "dependencies": [...],
        "semantic": {...}
    },
    "metrics": {
        "time_taken": "2.5s",
        "files_analyzed": 10
    }
}
```

## Next Steps

- [Pattern Catalog](patterns/index.md)
- [Quality Rules](quality/index.md)
- [CI/CD Setup](../integration/ci-cd.md)
- [Custom Rules Guide](rules/custom.md) 