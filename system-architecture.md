# TechPath System Architecture

This document outlines the architecture of the TechPath system, which consists of two main components:

1. A Python-based MCP (Model Context Protocol) server for codebase analysis
2. A React frontend web application for learning paths

## Overall System Architecture

```mermaid
graph TD
    subgraph "TechPath System"
        Frontend[React Frontend]
        Backend[MCP Server]
        
        Frontend -- API Calls --> Backend
        Backend -- API Responses --> Frontend
        
        subgraph "Data Storage"
            Supabase[(Supabase)]
            Qdrant[(Qdrant Vector DB)]
            FileSystem[(Local File System)]
        end
        
        Frontend <--> Supabase
        Backend <--> Qdrant
        Backend <--> FileSystem
    end
    
    subgraph "External Services"
        Claude[Claude API]
    end
    
    Backend <--> Claude
```

## MCP Server Architecture

The MCP (Model Context Protocol) server provides advanced codebase analysis capabilities to LLMs like Claude. It integrates with Qdrant vector database for semantic search across codebases.

```mermaid
graph TD
    subgraph "MCP Server Core Infrastructure"
        Server[CodebaseAnalysisServer]
        FastAPI[FastAPI Application]
        Config[ServerConfig]
        
        Server --> FastAPI
        Server --> Config
        
        subgraph "Core Components"
            VectorStore[Vector Store]
            Embedder[Sentence Transformer]
            ADRManager[ADR Manager]
            DebugSystem[Debug System]
            DocManager[Documentation Manager]
            KnowledgeBase[Knowledge Base]
            PromptManager[Prompt Manager]
            TaskManager[Task Manager]
        end
        
        Server --> VectorStore
        Server --> Embedder
        Server --> ADRManager
        Server --> DebugSystem
        Server --> DocManager
        Server --> KnowledgeBase
        Server --> PromptManager
        Server --> TaskManager
        
        TaskManager --> ADRManager
        TaskManager --> DebugSystem
        TaskManager --> DocManager
        TaskManager --> KnowledgeBase
        TaskManager --> PromptManager
    end
    
    subgraph "MCP API Endpoints"
        AnalyzeCode[/tools/analyze-code]
        CreateADR[/tools/create-adr]
        DebugIssue[/tools/debug-issue]
        CrawlDocs[/tools/crawl-docs]
        SearchKnowledge[/tools/search-knowledge]
        GetTask[/tools/get-task]
    end
    
    FastAPI --> AnalyzeCode
    FastAPI --> CreateADR
    FastAPI --> DebugIssue
    FastAPI --> CrawlDocs
    FastAPI --> SearchKnowledge
    FastAPI --> GetTask
    
    AnalyzeCode --> TaskManager
    CreateADR --> TaskManager
    DebugIssue --> TaskManager
    CrawlDocs --> TaskManager
    SearchKnowledge --> KnowledgeBase
    GetTask --> TaskManager
    
    VectorStore <--> Qdrant[(Qdrant Database)]
    DocManager <--> FileSystem[(File System)]
    KnowledgeBase <--> FileSystem
    ADRManager <--> FileSystem
```

## React Frontend Architecture

The TechPath React frontend is a web application designed to provide users with curated learning paths and resources for various technologies, with user authentication, content management, and community features.

```mermaid
graph TD
    subgraph "React Frontend"
        App[App.tsx]
        Router[React Router]
        
        subgraph "Context Providers"
            AuthProvider[AuthContext]
        end
        
        subgraph "UI Components"
            Navigation[Navigation]
            Pages[Page Components]
            SharedUI[Shared UI Components]
        end
        
        subgraph "Feature Components"
            Auth[Authentication Components]
            Admin[Admin Components]
            LearningPath[Learning Path Components]
            Portfolio[Portfolio Components]
            Community[Community Components]
        end
        
        App --> Router
        App --> AuthProvider
        Router --> Pages
        Router --> Auth
        Router --> Admin
        Router --> LearningPath
        Router --> Portfolio
        Router --> Community
        
        Pages --> Navigation
        Pages --> SharedUI
    end
    
    subgraph "External Services"
        SupabaseAuth[Supabase Auth]
        SupabaseDB[Supabase Database]
    end
    
    AuthProvider <--> SupabaseAuth
    Auth <--> SupabaseAuth
    Admin <--> SupabaseDB
    LearningPath <--> SupabaseDB
    Portfolio <--> SupabaseDB
    Community <--> SupabaseDB
```

## Data Flow Architecture

This diagram shows how data flows between different components of the system.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Supabase
    participant MCPServer
    participant Qdrant
    participant Claude
    
    User->>Frontend: Interacts with UI
    
    alt Authentication Flow
        Frontend->>Supabase: Auth Request
        Supabase-->>Frontend: Auth Response
        Frontend->>User: Auth Result
    end
    
    alt Learning Path Flow
        Frontend->>Supabase: Request Learning Paths
        Supabase-->>Frontend: Learning Path Data
        Frontend->>User: Display Learning Paths
    end
    
    alt Code Analysis Flow
        User->>Frontend: Submit Code for Analysis
        Frontend->>MCPServer: /tools/analyze-code
        MCPServer->>Qdrant: Vector Search
        MCPServer->>Claude: Code Analysis Request
        Claude-->>MCPServer: Analysis Results
        MCPServer-->>Frontend: Analysis Response
        Frontend->>User: Display Results
    end
    
    alt ADR Creation Flow
        User->>Frontend: Request ADR Creation
        Frontend->>MCPServer: /tools/create-adr
        MCPServer->>Claude: ADR Generation Request
        Claude-->>MCPServer: Generated ADR
        MCPServer-->>Frontend: ADR Response
        Frontend->>User: Display ADR
    end
```

## System Goals and Purpose

The TechPath system combines two distinct but complementary components:

1. **MCP Server (Backend)**:
   - Provides codebase analysis capabilities using vector search and LLM integration
   - Generates Architectural Decision Records (ADRs)
   - Offers systematic debugging using Agans' 9 Rules methodology
   - Manages technical documentation and knowledge retrieval
   - Serves as an AI-augmented development assistant

2. **React Frontend (Web Application)**:
   - Delivers structured learning paths for technology education
   - Manages user profiles and authentication
   - Provides portfolio showcase capabilities
   - Facilitates community interaction and networking
   - Offers administrative interfaces for content management

Together, these components create a comprehensive platform for both learning about technology and applying that knowledge in practical development scenarios with AI assistance.