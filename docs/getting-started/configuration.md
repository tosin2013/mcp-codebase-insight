# Configuration Guide

> 🚧 **Documentation In Progress**
> 
> This documentation is being actively developed. More details will be added soon.

## Configuration Methods

MCP Codebase Insight can be configured through:
1. Environment variables
2. Configuration file
3. Command-line arguments

Priority order (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

## Environment Variables

### Required Variables
```bash
# Server Configuration
MCP_HOST=127.0.0.1
MCP_PORT=3000

# Vector Store
QDRANT_URL=http://localhost:6333

# Storage Paths
MCP_DOCS_CACHE_DIR=./docs
MCP_ADR_DIR=./docs/adrs
MCP_KB_STORAGE_DIR=./knowledge
MCP_DISK_CACHE_DIR=./cache
```

### Optional Variables
```bash
# Logging
MCP_LOG_LEVEL=INFO
MCP_LOG_FORMAT=json

# Performance
MCP_CACHE_SIZE=1000
MCP_WORKER_COUNT=4
```

## Configuration File

Create `config.yaml` in your project root:

```yaml
server:
  host: 127.0.0.1
  port: 3000
  workers: 4

vector_store:
  url: http://localhost:6333
  collection: code_vectors

storage:
  docs_cache: ./docs
  adr_dir: ./docs/adrs
  kb_storage: ./knowledge
  disk_cache: ./cache

logging:
  level: INFO
  format: json
```

## Command-line Arguments

```bash
mcp-codebase-insight --help

Options:
  --host TEXT                 Server host address
  --port INTEGER             Server port
  --log-level TEXT           Logging level
  --debug                    Enable debug mode
  --config PATH              Path to config file
  --qdrant-url TEXT         Qdrant server URL
  --docs-dir PATH           Documentation directory
  --adr-dir PATH            ADR directory
  --kb-dir PATH             Knowledge base directory
  --cache-dir PATH          Cache directory
  --workers INTEGER         Number of workers
  --batch-size INTEGER      Batch size
  --timeout INTEGER         Request timeout
  --auth                    Enable authentication
  --metrics                 Enable metrics
  --help                    Show this message and exit
```

## Feature-specific Configuration

### 1. Vector Store Configuration

```yaml
vector_store:
  # Embedding model settings
  model:
    name: all-MiniLM-L6-v2
    dimension: 384
    normalize: true
  
  # Collection settings
  collection:
    name: mcp_vectors
    distance: Cosine
    on_disk: false
    
  # Search settings
  search:
    limit: 10
    threshold: 0.75
```

### 2. Documentation Management

```yaml
documentation:
  # Auto-generation settings
  auto_generate: true
  min_confidence: 0.8
  
  # Crawling settings
  crawl:
    max_depth: 3
    timeout: 30
    exclude_patterns: ["*.git*", "node_modules"]
    
  # Storage settings
  storage:
    format: markdown
    index_file: _index.md
```

### 3. ADR Management

```yaml
adr:
  # Template settings
  template_dir: templates/adr
  default_template: default.md
  
  # Workflow settings
  require_approval: true
  auto_number: true
  
  # Storage settings
  storage:
    format: markdown
    naming: date-title
```

## Environment-specific Configurations

### Development

```yaml
debug: true
log_level: DEBUG
metrics:
  enabled: false
vector_store:
  on_disk: false
```

### Production

```yaml
debug: false
log_level: INFO
security:
  auth_enabled: true
  allowed_origins: ["https://your-domain.com"]
metrics:
  enabled: true
vector_store:
  on_disk: true
```

### Testing

```yaml
debug: true
log_level: DEBUG
vector_store:
  collection_name: test_vectors
storage:
  docs_cache_dir: ./test/docs
```

## Best Practices

1. **Security**
   - Always enable authentication in production
   - Use environment variables for sensitive values
   - Restrict CORS origins in production

2. **Performance**
   - Adjust worker count based on CPU cores
   - Enable disk storage for large vector collections
   - Configure appropriate batch sizes

3. **Monitoring**
   - Enable metrics in production
   - Set appropriate log levels
   - Configure health check endpoints

4. **Storage**
   - Use absolute paths in production
   - Implement backup strategies
   - Monitor disk usage

## Validation

To validate your configuration:

```bash
mcp-codebase-insight validate-config --config config.yaml
```

## Troubleshooting

Common configuration issues and solutions:

1. **Permission Denied**
   ```bash
   # Fix directory permissions
   chmod -R 755 docs knowledge cache
   ```

2. **Port Already in Use**
   ```bash
   # Use different port
   export MCP_PORT=3001
   ```

3. **Memory Issues**
   ```yaml
   # Adjust batch size
   performance:
     batch_size: 50
   ```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [API Reference](../api/rest-api.md)
- [Development Guide](../development/README.md)
