# Documentation Management

MCP Codebase Insight provides powerful tools for managing technical documentation, ensuring it stays up-to-date with your codebase and is easily accessible.

## Overview

The documentation management feature:
- Auto-generates documentation from code
- Maintains documentation-code links
- Provides semantic search capabilities
- Supports multiple documentation formats
- Enables documentation validation
- Tracks documentation coverage

## Features

### 1. Documentation Generation

Automatically generate documentation from code:

```python
# Example: Generate documentation for a module
response = await client.post(
    "http://localhost:3000/api/docs/generate",
    json={
        "source": "src/auth/",
        "output_format": "markdown",
        "include_private": False,
        "template": "api-docs"
    }
)

docs = response.json()
print(f"Generated {len(docs['files'])} documentation files")
```

### 2. Documentation Search

Search through documentation using semantic understanding:

```python
# Example: Search documentation
response = await client.get(
    "http://localhost:3000/api/docs/search",
    params={
        "query": "how to implement authentication",
        "doc_types": ["guide", "api", "tutorial"],
        "limit": 5
    }
)

results = response.json()
for doc in results["matches"]:
    print(f"- {doc['title']} (Score: {doc['score']})")
```

### 3. Documentation Validation

Validate documentation completeness and accuracy:

```python
# Example: Validate documentation
response = await client.post(
    "http://localhost:3000/api/docs/validate",
    json={
        "paths": ["docs/api/", "docs/guides/"],
        "rules": ["broken-links", "code-coverage", "freshness"]
    }
)

validation = response.json()
print(f"Found {len(validation['issues'])} issues")
```

### 4. Documentation Crawling

Crawl and index external documentation:

```python
# Example: Crawl documentation
response = await client.post(
    "http://localhost:3000/api/docs/crawl",
    json={
        "urls": [
            "https://api.example.com/docs",
            "https://wiki.example.com/technical-docs"
        ],
        "depth": 2,
        "include_patterns": ["*.md", "*.html"],
        "exclude_patterns": ["*draft*", "*private*"]
    }
)
```

## Usage

### Basic Documentation Workflow

1. **Generate Documentation**
   ```bash
   # Using CLI
   mcp-codebase-insight docs generate \
       --source src/ \
       --output docs/api \
       --template api-reference
   ```

2. **Validate Documentation**
   ```bash
   # Check documentation quality
   mcp-codebase-insight docs validate \
       --path docs/ \
       --rules all
   ```

3. **Update Documentation**
   ```bash
   # Update existing documentation
   mcp-codebase-insight docs update \
       --path docs/api \
       --sync-with-code
   ```

4. **Search Documentation**
   ```bash
   # Search in documentation
   mcp-codebase-insight docs search \
       "authentication implementation" \
       --type guide \
       --limit 5
   ```

### Documentation Templates

Create custom documentation templates:

```yaml
# templates/docs/api-reference.yaml
name: "API Reference Template"
sections:
  - title: "Overview"
    required: true
    content:
      - "Brief description"
      - "Key features"
      - "Requirements"
  
  - title: "Installation"
    required: true
    content:
      - "Step-by-step instructions"
      - "Configuration options"
  
  - title: "API Methods"
    required: true
    for_each: "method"
    content:
      - "Method signature"
      - "Parameters"
      - "Return values"
      - "Examples"
```

## Configuration

### Documentation Settings

```yaml
documentation:
  # Generation settings
  generation:
    templates_dir: "./templates/docs"
    output_dir: "./docs"
    default_format: "markdown"
    include_private: false
    
  # Validation settings
  validation:
    rules:
      broken_links: true
      code_coverage: true
      freshness: true
    max_age_days: 90
    
  # Search settings
  search:
    index_update_interval: "1h"
    min_score: 0.5
    max_results: 10
    
  # Crawling settings
  crawling:
    max_depth: 3
    timeout: 30
    concurrent_requests: 5
    respect_robots_txt: true
```

### Storage Settings

```yaml
storage:
  # File storage
  files:
    path: "./docs"
    backup_path: "./docs/backup"
    
  # Vector storage
  vectors:
    collection: "documentation"
    dimension: 384
    
  # Cache settings
  cache:
    enabled: true
    ttl: 3600
    max_size: "1GB"
```

## Best Practices

1. **Documentation Structure**
   - Use consistent formatting
   - Follow a clear hierarchy
   - Include examples
   - Keep sections focused

2. **Maintenance**
   - Update regularly
   - Remove outdated content
   - Track changes with code
   - Validate links

3. **Organization**
   - Use clear categories
   - Maintain an index
   - Cross-reference related docs
   - Version appropriately

4. **Quality**
   - Include code examples
   - Add diagrams where helpful
   - Proofread content
   - Test code samples

## API Reference

### Documentation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/docs/generate` | POST | Generate documentation |
| `/api/docs/validate` | POST | Validate documentation |
| `/api/docs/search` | GET | Search documentation |
| `/api/docs/crawl` | POST | Crawl external docs |
| `/api/docs/update` | POST | Update documentation |
| `/api/docs/stats` | GET | Get documentation stats |

### Response Format

```json
{
    "documentation": {
        "id": "uuid",
        "title": "string",
        "content": "string",
        "format": "string",
        "metadata": {
            "author": "string",
            "created_at": "datetime",
            "updated_at": "datetime",
            "version": "string"
        },
        "related_code": [{
            "file": "string",
            "lines": [int, int],
            "type": "string"
        }],
        "validation": {
            "status": "string",
            "issues": [{
                "type": "string",
                "severity": "string",
                "message": "string"
            }]
        }
    }
}
```

## Integration

### IDE Integration

```python
# VS Code Extension Example
from mcp.client import Client

client = Client.connect()

# Document current file
async def document_current_file(file_path: str):
    response = await client.post(
        "/api/docs/generate",
        json={
            "source": file_path,
            "template": "code-reference"
        }
    )
    return response.json()
```

### CI/CD Integration

```yaml
# GitHub Actions Example
name: Documentation Check

on: [push, pull_request]

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Documentation
        run: |
          curl -X POST http://localhost:3000/api/docs/validate \
            -H "Content-Type: application/json" \
            -d '{
              "paths": ["docs/"],
              "rules": ["all"]
            }'
```

## Troubleshooting

### Common Issues

1. **Generation Fails**
   ```bash
   # Check template validity
   mcp-codebase-insight docs validate-template \
       --template api-reference
   ```

2. **Search Not Working**
   ```bash
   # Rebuild search index
   mcp-codebase-insight docs rebuild-index
   ```

3. **Validation Errors**
   ```bash
   # Get detailed validation report
   mcp-codebase-insight docs validate \
       --path docs/ \
       --verbose
   ```

## Next Steps

- [Documentation Templates](docs/templates.md)
- [Style Guide](docs/style-guide.md)
- [Advanced Search](docs/search.md)
- [Automation Guide](docs/automation.md) 