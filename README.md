# MCP Codebase Insight

MCP Codebase Insight is a server component of the Model Context Protocol (MCP) that provides intelligent analysis and insights into codebases. It uses vector search and machine learning to understand code patterns, architectural decisions, and documentation.

## Target Audience

MCP Codebase Insight is designed primarily for:

- **Software Developers**: Who want AI-assisted code analysis and improvements
- **Software Architects**: Managing architecture decisions and technical documentation
- **DevOps Engineers**: Monitoring system health and integrating with CI/CD pipelines
- **Technical Leads**: Ensuring best practices and maintaining knowledge management
- **Data Scientists**: Who can leverage the system for code pattern analysis

This tool is most valuable for teams working on complex codebases that require consistent patterns, architectural oversight, and thorough documentation.

## Features

- **Code Analysis**: Identify patterns, vulnerabilities, and optimization opportunities
- **ADR Management**: Track architectural decisions with context
- **Documentation**: Auto-generate and maintain technical documentation
- **Knowledge Base**: Store reusable code patterns and solutions
- **Debug System**: Analyze and fix issues with context awareness
- **Build Verification**: Automated end-to-end build verification

## How It Works

MCP Codebase Insight operates through a pipeline of intelligent analysis:

1. **Code Ingestion**: The system analyzes your codebase, parsing files and understanding their structure.
2. **Embedding Generation**: Code, documentation, and architectural decisions are converted into vector embeddings.
3. **Vector Storage**: These embeddings are stored in a Qdrant vector database, enabling semantic search and relationship mapping.
4. **Contextual Analysis**: When queried, the system retrieves relevant context from the vector database and applies specialized models to generate insights.
5. **Action Generation**: Based on analysis, the system can recommend actions, generate documentation, or provide debugging assistance.

![System Architecture](https://via.placeholder.com/800x400?text=MCP+Codebase+Insight+Architecture)

*Note: The above URL is a placeholder for an architecture diagram. Replace with an actual diagram path.*

## Quick Start

For detailed installation and usage instructions, please refer to our [documentation](./docs/README.md).

> **Important Requirement**: MCP Codebase Insight requires a running Qdrant vector database instance to function properly. See [Qdrant Setup](./docs/getting-started/installation.md#qdrant-setup) for installation instructions.

### Basic Installation

```bash
# Install the package
pip install mcp-codebase-insight

# Set up basic environment variables
export MCP_HOST=127.0.0.1
export MCP_PORT=3000
export QDRANT_URL=http://localhost:6333
export MCP_DOCS_CACHE_DIR=./docs
export MCP_ADR_DIR=./docs/adrs
export MCP_KB_STORAGE_DIR=./knowledge
export MCP_DISK_CACHE_DIR=./cache

# Start the server
mcp-codebase-insight --host 127.0.0.1 --port 3000 --log-level INFO
```

> **Note:** For a complete list of environment variables and configuration options, see the [Configuration Guide](./docs/getting-started/configuration.md).

### Using Docker

```bash
docker run -p 3000:3000 \
    --env-file .env \
    -v $(pwd)/docs:/app/docs \
    -v $(pwd)/knowledge:/app/knowledge \
    tosin2013/mcp-codebase-insight
```

## Documentation

For complete documentation, please see the [docs directory](./docs/):

- [Installation Guide](./docs/getting-started/installation.md)
- [Configuration Guide](./docs/getting-started/configuration.md)
- [API Reference](./docs/usage/api-reference.md)
- [IDE Integration](./docs/usage/ide-integration.md)
- [Development Guide](./docs/development/contributing.md)
- [Troubleshooting](./docs/troubleshooting/common-issues.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issue Tracker](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
- [Discussions](https://github.com/modelcontextprotocol/mcp-codebase-insight/discussions)
