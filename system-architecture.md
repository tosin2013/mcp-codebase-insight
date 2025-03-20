# System Architecture - MCP Codebase Insight

This document outlines the system architecture of the MCP Codebase Insight project using various diagrams to illustrate different aspects of the system.

## High-Level System Architecture

```mermaid
graph TB
    Client[Client Applications] --> API[FastAPI Server]
    API --> Core[Core Services]
    
    subgraph Core Services
        CodeAnalysis[Code Analysis Service]
        ADR[ADR Management]
        Doc[Documentation Service]
        Knowledge[Knowledge Base]
        Debug[Debug System]
        Metrics[Metrics & Health]
        Cache[Caching System]
    end
    
    Core --> VectorDB[(Qdrant Vector DB)]
    Core --> FileSystem[(File System)]
    
    CodeAnalysis --> VectorDB
    Knowledge --> VectorDB
    ADR --> FileSystem
    Doc --> FileSystem
```

## Component Relationships

```mermaid
graph LR
    subgraph Core Components
        Embeddings[Embeddings Service]
        VectorStore[Vector Store Service]
        Knowledge[Knowledge Service]
        Tasks[Tasks Service]
        Prompts[Prompts Service]
        Debug[Debug Service]
        Health[Health Service]
        Config[Config Service]
        Cache[Cache Service]
    end
    
    Embeddings --> VectorStore
    Knowledge --> VectorStore
    Knowledge --> Embeddings
    Tasks --> Knowledge
    Debug --> Knowledge
    Prompts --> Tasks
    Health --> Cache
    Config --> |Configures| Core Components
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Knowledge
    participant Embeddings
    participant VectorStore
    participant Cache
    
    Client->>API: Request Analysis
    API->>Cache: Check Cache
    alt Cache Hit
        Cache-->>API: Return Cached Result
    else Cache Miss
        API->>Knowledge: Process Request
        Knowledge->>Embeddings: Generate Embeddings
        Embeddings->>VectorStore: Store/Query Vectors
        VectorStore-->>Knowledge: Vector Results
        Knowledge-->>API: Analysis Results
        API->>Cache: Store Results
        API-->>Client: Return Results
    end
```

## Directory Structure

```mermaid
graph TD
    Root[mcp-codebase-insight] --> Src[src/]
    Root --> Tests[tests/]
    Root --> Docs[docs/]
    Root --> Scripts[scripts/]
    Root --> Knowledge[knowledge/]
    
    Src --> Core[core/]
    Src --> Utils[utils/]
    
    Core --> Components{Core Components}
    Components --> ADR[adr.py]
    Components --> Cache[cache.py]
    Components --> Config[config.py]
    Components --> Debug[debug.py]
    Components --> Doc[documentation.py]
    Components --> Embed[embeddings.py]
    Components --> Know[knowledge.py]
    Components --> Vector[vector_store.py]
    
    Knowledge --> Patterns[patterns/]
    Knowledge --> Tasks[tasks/]
    Knowledge --> Prompts[prompts/]
```

## Security and Authentication Flow

```mermaid
graph TD
    Request[Client Request] --> Auth[Authentication Layer]
    Auth --> Validation[Request Validation]
    Validation --> RateLimit[Rate Limiting]
    RateLimit --> Processing[Request Processing]
    
    subgraph Security Measures
        Auth
        Validation
        RateLimit
        Logging[Audit Logging]
    end
    
    Processing --> Logging
    Processing --> Response[API Response]
```

This architecture documentation illustrates the main components and their interactions within the MCP Codebase Insight system. The system is designed to be modular, scalable, and maintainable, with clear separation of concerns between different components.

Key architectural decisions:
1. Use of FastAPI for high-performance API endpoints
2. Vector database (Qdrant) for efficient similarity search
3. Modular core services for different functionalities
4. Caching layer for improved performance
5. Clear separation between data storage and business logic
6. Comprehensive security measures
7. Structured knowledge management system 