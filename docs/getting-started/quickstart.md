# Quick Start Tutorial

This tutorial will help you get started with MCP Codebase Insight quickly. We'll cover basic setup and essential features.

## Prerequisites

Ensure you have:
- Python 3.11 or higher
- pip (Python package installer)
- Git
- Docker (optional, for containerized setup)

## 5-Minute Setup

1. **Install MCP Codebase Insight**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install the package
   pip install mcp-codebase-insight
   ```

2. **Start Qdrant Vector Database**
   ```bash
   # Using Docker (recommended)
   docker pull qdrant/qdrant
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. **Configure Environment**
   ```bash
   # Create .env file
   cat > .env << EOL
   MCP_HOST=127.0.0.1
   MCP_PORT=3000
   QDRANT_URL=http://localhost:6333
   MCP_DOCS_CACHE_DIR=./docs
   MCP_ADR_DIR=./docs/adrs
   MCP_KB_STORAGE_DIR=./knowledge
   EOL
   
   # Create required directories
   mkdir -p docs/adrs knowledge
   ```

4. **Start the Server**
   ```bash
   mcp-codebase-insight --host 127.0.0.1 --port 3000
   ```

5. **Verify Installation**
   ```bash
   # In another terminal
   curl http://localhost:3000/health
   ```

## Basic Usage Examples

### 1. Analyze Code Patterns

```python
import httpx

async with httpx.AsyncClient() as client:
    # Analyze code patterns
    response = await client.post(
        "http://localhost:3000/api/analyze",
        json={
            "code": """
            def calculate_fibonacci(n):
                if n <= 1:
                    return n
                return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
            """,
            "language": "python"
        }
    )
    
    results = response.json()
    print("Detected patterns:", results["patterns"])
```

### 2. Create an ADR

```python
# Create an Architecture Decision Record
response = await client.post(
    "http://localhost:3000/api/adrs",
    json={
        "title": "Use FastAPI for REST API",
        "context": {
            "problem": "Need a modern Python web framework",
            "constraints": ["Performance", "Easy to maintain"]
        },
        "options": [
            {
                "title": "FastAPI",
                "pros": ["Fast", "Modern", "Great docs"],
                "cons": ["Newer framework"]
            },
            {
                "title": "Flask",
                "pros": ["Mature", "Simple"],
                "cons": ["Slower", "Less modern"]
            }
        ],
        "decision": "We will use FastAPI",
        "consequences": ["Need to learn async/await", "Better performance"]
    }
)

adr = response.json()
print(f"Created ADR: {adr['id']}")
```

### 3. Search Documentation

```python
# Search for relevant documentation
response = await client.get(
    "http://localhost:3000/api/docs/search",
    params={
        "query": "how to handle authentication",
        "limit": 5
    }
)

docs = response.json()
for doc in docs["results"]:
    print(f"- {doc['title']}: {doc['relevance_score']}")
```

### 4. Monitor System Health

```python
# Get system health status
response = await client.get("http://localhost:3000/health")
health = response.json()

print("System Status:", health["status"])
for component, status in health["components"].items():
    print(f"- {component}: {status['status']}")
```

## Using the Web Interface

1. Open your browser to `http://localhost:3000/docs`
2. Explore the interactive API documentation
3. Try out different endpoints directly from the browser

## Next Steps

1. **Explore Advanced Features**
   - [Code Analysis Guide](../features/code-analysis.md)
   - [ADR Management](../features/adr-management.md)
   - [Documentation Management](../features/documentation.md)

2. **Configure for Production**
   - [Security Setup](../security/security-guide.md)
   - [Production Deployment](../deployment/production.md)
   - [Monitoring](../deployment/monitoring.md)

3. **Integrate with Tools**
   - [IDE Integration](../integration/ide-setup.md)
   - [CI/CD Pipeline](../integration/ci-cd.md)
   - [Custom Extensions](../integration/extensions.md)

## Common Operations

### Managing ADRs

```bash
# List all ADRs
curl http://localhost:3000/api/adrs

# Get specific ADR
curl http://localhost:3000/api/adrs/{adr_id}

# Update ADR status
curl -X PATCH http://localhost:3000/api/adrs/{adr_id} \
    -H "Content-Type: application/json" \
    -d '{"status": "ACCEPTED"}'
```

### Working with Documentation

```bash
# Crawl documentation
curl -X POST http://localhost:3000/api/docs/crawl \
    -H "Content-Type: application/json" \
    -d '{
        "urls": ["https://your-docs-site.com"],
        "source_type": "documentation"
    }'

# Search documentation
curl "http://localhost:3000/api/docs/search?query=authentication&limit=5"
```

### Analyzing Code

```bash
# Analyze code patterns
curl -X POST http://localhost:3000/api/analyze \
    -H "Content-Type: application/json" \
    -d '{
        "code": "your code here",
        "language": "python"
    }'

# Get analysis results
curl http://localhost:3000/api/analysis/{analysis_id}
```

## Troubleshooting

1. **Server Won't Start**
   ```bash
   # Check if ports are in use
   lsof -i :3000
   lsof -i :6333
   ```

2. **Connection Issues**
   ```bash
   # Verify Qdrant is running
   curl http://localhost:6333/health
   
   # Check MCP server health
   curl http://localhost:3000/health
   ```

3. **Permission Problems**
   ```bash
   # Fix directory permissions
   chmod -R 755 docs knowledge
   ```

## Getting Help

- Check the [Troubleshooting Guide](../troubleshooting/common-issues.md)
- Join our [Discussion Forum](https://github.com/modelcontextprotocol/mcp-codebase-insight/discussions)
- Open an [Issue](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues) 