# Troubleshooting Guide

> 🚧 **Documentation In Progress**
> 
> This documentation is being actively developed. More details will be added soon.

## Common Issues

### Installation Issues

#### 1. Dependencies Installation Fails
```bash
Error: Failed building wheel for sentence-transformers
```

**Solution:**
```bash
# Update pip and install wheel
pip install --upgrade pip
pip install wheel

# Try installing with specific version
pip install sentence-transformers==2.2.2

# If still failing, install system dependencies
# Ubuntu/Debian:
sudo apt-get install python3-dev build-essential
# CentOS/RHEL:
sudo yum install python3-devel gcc
```

#### 2. Permission Denied
```bash
PermissionError: [Errno 13] Permission denied: '/usr/local/lib/python3.11/site-packages'
```

**Solution:**
```bash
# Install in user space
pip install --user mcp-codebase-insight

# Or fix directory permissions
sudo chown -R $USER:$USER venv/
```

### Server Issues

#### 1. Port Already in Use
```bash
[Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using the port
lsof -i :3000  # On Linux/macOS
netstat -ano | findstr :3000  # On Windows

# Kill the process
kill -9 <PID>

# Or use a different port
mcp-codebase-insight --port 3001
```

#### 2. Server Won't Start
```bash
ERROR:    [Errno 2] No such file or directory: './docs'
```

**Solution:**
```bash
# Create required directories
mkdir -p docs/adrs knowledge cache

# Fix permissions
chmod -R 755 docs knowledge cache
```

### Vector Store Issues

#### 1. Qdrant Connection Failed
```bash
ConnectionError: Failed to connect to Qdrant server
```

**Solution:**
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Start Qdrant if not running
docker start qdrant

# Verify environment variable
echo $QDRANT_URL
# Should be: http://localhost:6333
```

#### 2. Collection Creation Failed
```bash
Error: Collection 'code_vectors' already exists
```

**Solution:**
```bash
# List existing collections
curl http://localhost:6333/collections

# Delete existing collection if needed
curl -X DELETE http://localhost:6333/collections/code_vectors

# Create new collection with correct parameters
python -c "
from qdrant_client import QdrantClient
client = QdrantClient('localhost', port=6333)
client.recreate_collection(
    collection_name='code_vectors',
    vectors_config={'size': 384, 'distance': 'Cosine'}
)
"
```

### Memory Issues

#### 1. Out of Memory
```bash
MemoryError: Unable to allocate array with shape (1000000, 384)
```

**Solution:**
```yaml
# Adjust batch size in config.yaml
vector_store:
  batch_size: 100  # Reduce from default

# Or set environment variable
export MCP_BATCH_SIZE=100
```

#### 2. Slow Performance
```bash
WARNING: Vector search taking longer than expected
```

**Solution:**
```yaml
# Enable disk storage in config.yaml
vector_store:
  on_disk: true
  
# Adjust cache size
performance:
  cache_size: 1000
```

### Documentation Issues

#### 1. Documentation Map Failed
```bash
Error: Unable to create documentation map: Invalid directory structure
```

**Solution:**
```bash
# Verify directory structure
tree docs/

# Create required structure
mkdir -p docs/{adrs,api,components}
touch docs/index.md
```

#### 2. Search Not Working
```bash
Error: Search index not found
```

**Solution:**
```bash
# Rebuild search index
curl -X POST http://localhost:3000/api/docs/rebuild-index

# Verify index exists
ls -l docs/.search_index
```

## Debugging Tips

### 1. Enable Debug Logging
```bash
# Set environment variable
export MCP_LOG_LEVEL=DEBUG

# Or use command line flag
mcp-codebase-insight --debug
```

### 2. Check System Resources
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check CPU usage
top
```

### 3. Verify Configuration
```bash
# Print current config
mcp-codebase-insight show-config

# Validate config file
mcp-codebase-insight validate-config --config config.yaml
```

## Getting Help

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
2. Join our [Discussion Forum](https://github.com/modelcontextprotocol/mcp-codebase-insight/discussions)
3. Review the [FAQ](faq.md)
4. Contact Support:
   - Discord: [Join Server](https://discord.gg/mcp-codebase-insight)
   - Email: support@mcp-codebase-insight.org

## Next Steps

- [Installation Guide](../getting-started/installation.md)
- [Configuration Guide](../getting-started/configuration.md)
- [Development Guide](../development/README.md) 