# Frequently Asked Questions

> 🚧 **Documentation In Progress**
> 
> This documentation is being actively developed. More details will be added soon.

## General Questions

### What is MCP Codebase Insight?
MCP Codebase Insight is a tool for analyzing and understanding codebases through semantic analysis, pattern detection, and documentation management.

### What are the system requirements?
- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Docker (optional, for containerized deployment)

### Which operating systems are supported?
- Linux (Ubuntu 20.04+, CentOS 8+)
- macOS (10.15+)
- Windows 10/11 with WSL2

## Installation

### Do I need to install Qdrant separately?
Yes, Qdrant is required for vector storage. You can install it via Docker (recommended) or from source. See the [Qdrant Setup Guide](../getting-started/qdrant_setup.md).

### Can I use a different vector database?
Currently, only Qdrant is supported. Support for other vector databases may be added in future releases.

### Why am I getting permission errors during installation?
This usually happens when trying to install in system directories. Try:
1. Using a virtual environment
2. Installing with `--user` flag
3. Using proper permissions for directories

## Usage

### How do I start analyzing my codebase?
1. Install MCP Codebase Insight
2. Set up Qdrant
3. Configure your environment
4. Run the server
5. Use the API or CLI to analyze your code

### Can I analyze multiple repositories at once?
Yes, you can analyze multiple repositories by:
1. Using batch analysis
2. Creating separate collections
3. Merging results afterward

### How do I customize the analysis?
You can customize:
- Analysis patterns
- Vector search parameters
- Documentation generation
- Output formats

See the [Configuration Guide](../getting-started/configuration.md).

## Performance

### Why is vector search slow?
Common reasons:
1. Large vector collection
2. Limited memory
3. Network latency
4. Insufficient CPU resources

Solutions:
1. Enable disk storage
2. Adjust batch size
3. Optimize search parameters
4. Scale hardware resources

### How much memory do I need?
Memory requirements depend on:
- Codebase size
- Vector collection size
- Batch processing size
- Concurrent operations

Minimum: 4GB RAM
Recommended: 8GB+ RAM

### Can I run it in production?
Yes, but consider:
1. Setting up authentication
2. Configuring CORS
3. Using SSL/TLS
4. Implementing monitoring
5. Setting up backups

## Features

### Does it support my programming language?
Currently supported:
- Python
- JavaScript/TypeScript
- Java
- Go
- Ruby

More languages planned for future releases.

### Can it generate documentation?
Yes, it can:
1. Generate API documentation
2. Create architecture diagrams
3. Maintain ADRs
4. Build knowledge bases

### How does pattern detection work?
Pattern detection uses:
1. Vector embeddings
2. AST analysis
3. Semantic search
4. Machine learning models

## Integration

### Can I integrate with my IDE?
Yes, through:
1. REST API
2. Language Server Protocol
3. Custom extensions

### Does it work with CI/CD pipelines?
Yes, you can:
1. Run analysis in CI
2. Generate reports
3. Enforce patterns
4. Update documentation

### Can I use it with existing tools?
Integrates with:
1. Git
2. Documentation generators
3. Code quality tools
4. Issue trackers

## Troubleshooting

### Where are the log files?
Default locations:
- Server logs: `./logs/server.log`
- Access logs: `./logs/access.log`
- Debug logs: `./logs/debug.log`

### How do I report bugs?
1. Check [existing issues](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
2. Create new issue with:
   - Clear description
   - Steps to reproduce
   - System information
   - Log files

### How do I get support?
Support options:
1. [Documentation](../README.md)
2. [GitHub Issues](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
3. [Discussion Forum](https://github.com/modelcontextprotocol/mcp-codebase-insight/discussions)
4. [Discord Community](https://discord.gg/mcp-codebase-insight)

## Next Steps

- [Common Issues](common-issues.md)
- [Installation Guide](../getting-started/installation.md)
- [Configuration Guide](../getting-started/configuration.md) 