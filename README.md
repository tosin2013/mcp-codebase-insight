# MCP Codebase Insight

> 🚧 **Development in Progress** 
> 
> This project is actively under development. Features and documentation are being continuously updated.

## Overview

MCP Codebase Insight is a system for analyzing and understanding codebases through semantic analysis, pattern detection, and documentation management.

## Current Development Status

### Completed Features
- ✅ Core Vector Store System
- ✅ Basic Knowledge Base
- ✅ SSE Integration
- ✅ Testing Framework

### In Progress
- 🔄 Documentation Management System
- 🔄 Advanced Pattern Detection
- 🔄 Performance Optimization
- 🔄 Integration Testing

### Planned
- 📋 Extended API Documentation
- 📋 Custom Pattern Plugins
- 📋 Advanced Caching Strategies
- 📋 Deployment Guides

## Workflows

### User Workflows

1. **Code Analysis**
   ```mermaid
   graph TD
       A[Developer] -->|Submit Code| B[Analysis Request]
       B --> C{Analysis Type}
       C -->|Pattern Detection| D[Pattern Analysis]
       C -->|Semantic Search| E[Vector Search]
       C -->|Documentation| F[Doc Analysis]
       D --> G[Results]
       E --> G
       F --> G
       G -->|Display| A
   ```

2. **Documentation Management**
   ```mermaid
   graph TD
       A[Developer] -->|Create/Update| B[Documentation]
       B --> C{Doc Type}
       C -->|ADR| D[ADR Processing]
       C -->|API| E[API Docs]
       C -->|Guide| F[User Guide]
       D --> G[Link Analysis]
       E --> G
       F --> G
       G -->|Update| H[Doc Map]
       H -->|Validate| A
   ```

3. **Testing Flow**
   ```mermaid
   graph TD
       A[Developer] -->|Run Tests| B[Test Suite]
       B --> C{Test Type}
       C -->|Unit| D[Unit Tests]
       C -->|Integration| E[Integration Tests]
       C -->|SSE| F[SSE Tests]
       D --> G[Results]
       E --> G
       F --> G
       G -->|Report| A
   ```

### System Workflows

1. **Vector Store Operations**
   ```mermaid
   sequenceDiagram
       participant User
       participant Server
       participant Cache
       participant VectorStore
       participant Knowledge
       
       User->>Server: Request Analysis
       Server->>Cache: Check Cache
       Cache-->>Server: Cache Hit/Miss
       
       alt Cache Miss
           Server->>VectorStore: Generate Embeddings
           VectorStore->>Knowledge: Get Patterns
           Knowledge-->>VectorStore: Return Patterns
           VectorStore-->>Server: Return Results
           Server->>Cache: Update Cache
       end
       
       Server-->>User: Return Analysis
   ```

2. **Health Monitoring**
   ```mermaid
   sequenceDiagram
       participant Monitor
       participant Components
       participant Tasks
       participant Alerts
       
       loop Every 30s
           Monitor->>Components: Check Status
           Components->>Tasks: Verify Tasks
           Tasks-->>Components: Task Status
           
           alt Issues Detected
               Components->>Alerts: Raise Alert
               Alerts->>Monitor: Alert Status
           end
           
           Components-->>Monitor: System Status
       end
   ```

## Quick Start

1. **Installation**
   ```bash
   pip install mcp-codebase-insight
   ```

2. **Basic Usage**
   ```python
   from mcp_codebase_insight import CodebaseAnalyzer
   
   analyzer = CodebaseAnalyzer()
   results = analyzer.analyze_code("path/to/code")
   ```

3. **Running Tests**
   ```bash
   pytest tests/
   ```

## Documentation

- [System Architecture](docs/system_architecture/README.md)
- [Core Components](docs/components/README.md)
- [API Reference](docs/api/README.md)
- [Development Guide](docs/development/README.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issue Tracker](https://github.com/modelcontextprotocol/mcp-codebase-insight/issues)
- [Discussions](https://github.com/modelcontextprotocol/mcp-codebase-insight/discussions)
