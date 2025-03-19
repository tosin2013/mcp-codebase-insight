import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional, List
from datetime import datetime
import time

from mcp.server import Server
from mcp.server.fastmcp import Context, FastMCP
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from .core import (
    ServerConfig,
    EmbeddingProvider,
    VectorStore,
    CacheManager,
    HealthMonitor,
    MetricsCollector,
    ErrorContext,
    handle_error
)
from .utils.logger import get_logger

logger = get_logger(__name__)

class CodebaseAnalyzer:
    """Analyzes code patterns and architecture."""
    
    def __init__(
        self, 
        vector_store: VectorStore,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector
    ):
        self.vector_store = vector_store
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
    
    async def analyze_patterns(self, code_text: str) -> Dict[str, Any]:
        """Analyze code patterns in the given text."""
        start_time = time.time()
        
        try:
            # Try cache first
            cached_result = await self.cache_manager.result_cache.get_result(
                "analyze_patterns", code_text
            )
            if cached_result:
                await self.metrics_collector.record_cache_access(hit=True)
                return cached_result
            
            await self.metrics_collector.record_cache_access(hit=False)
            
            # Get embedding
            vector = await self.vector_store.embed_text(code_text)
            await self.metrics_collector.record_vector_query()
            
            # Search for similar patterns
            similar_patterns = await self.vector_store.search(
                vector,
                filter_params={"must": [{"key": "type", "match": {"value": "pattern"}}]},
                limit=5
            )
            
            result = {
                "patterns_found": len(similar_patterns),
                "matches": [
                    {
                        "pattern": p.payload.get("pattern_name", "Unknown"),
                        "description": p.payload.get("description", ""),
                        "similarity": p.score,
                        "examples": p.payload.get("examples", [])
                    }
                    for p in similar_patterns
                ]
            }
            
            # Cache the result
            await self.cache_manager.result_cache.store_result(
                "analyze_patterns",
                result,
                code_text
            )
            
            # Record metrics
            duration = time.time() - start_time
            await self.metrics_collector.record_request(
                tool_name="analyze_patterns",
                duration=duration,
                success=True,
                metadata={
                    "patterns_found": len(similar_patterns)
                }
            )
            
            return result
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            await self.metrics_collector.record_request(
                tool_name="analyze_patterns",
                duration=duration,
                success=False,
                error=str(e)
            )
            raise

    async def detect_architecture(self, codebase_path: str) -> Dict[str, Any]:
        """Detect architectural patterns in a codebase."""
        start_time = time.time()
        
        try:
            # Try cache first
            cached_result = await self.cache_manager.result_cache.get_result(
                "detect_architecture", codebase_path
            )
            if cached_result:
                await self.metrics_collector.record_cache_access(hit=True)
                return cached_result
            
            await self.metrics_collector.record_cache_access(hit=False)
            
            # This is a placeholder - actual implementation would analyze
            # the entire codebase structure
            result = {
                "architecture": "layered",
                "patterns": ["MVC", "Repository"],
                "components": ["controllers", "models", "views"]
            }
            
            # Cache the result
            await self.cache_manager.result_cache.store_result(
                "detect_architecture",
                result,
                codebase_path
            )
            
            # Record metrics
            duration = time.time() - start_time
            await self.metrics_collector.record_request(
                tool_name="detect_architecture",
                duration=duration,
                success=True
            )
            
            return result
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            await self.metrics_collector.record_request(
                tool_name="detect_architecture",
                duration=duration,
                success=False,
                error=str(e)
            )
            raise

@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[Dict]:
    """Initialize server components and manage their lifecycle."""
    config = ServerConfig.from_env()
    cache_manager = None
    health_monitor = None
    metrics_collector = None
    
    try:
        # Initialize vector store
        embedding_model = SentenceTransformer(config.embedding_model)
        embedder = EmbeddingProvider(embedding_model)
        
        # Initialize Qdrant client
        qdrant_client = QdrantClient(
            url=config.qdrant_url,
            timeout=config.qdrant_timeout
        )
        vector_store = VectorStore(qdrant_client, embedder, config.collection_name)
        await vector_store.initialize()
        
        # Initialize supporting components
        cache_manager = CacheManager(config.to_dict())
        health_monitor = HealthMonitor(config)
        metrics_collector = MetricsCollector()
        
        # Initialize analyzer
        analyzer = CodebaseAnalyzer(
            vector_store=vector_store,
            cache_manager=cache_manager,
            metrics_collector=metrics_collector
        )
        
        yield {
            "config": config,
            "vector_store": vector_store,
            "cache_manager": cache_manager,
            "health_monitor": health_monitor,
            "metrics_collector": metrics_collector,
            "analyzer": analyzer
        }
    
    finally:
        if vector_store:
            await vector_store.close()
        if cache_manager:
            await cache_manager.clear_all()
        if metrics_collector:
            await metrics_collector.reset()

# Create FastMCP instance with lifespan management
mcp = FastMCP(lifespan=server_lifespan)

# Tool Schemas
analyze_patterns_schema = {
    "type": "object",
    "properties": {
        "code": {
            "type": "string",
            "description": "Code text to analyze for patterns",
        }
    },
    "required": ["code"],
}

detect_architecture_schema = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Path to the codebase to analyze",
        }
    },
    "required": ["path"],
}

health_check_schema = {
    "type": "object",
    "properties": {
        "force": {
            "type": "boolean",
            "description": "Force a new health check",
            "default": False
        }
    }
}

metrics_schema = {
    "type": "object",
    "properties": {}
}

# Tool Implementations
@mcp.tool(name="analyze-patterns", description="Analyze code for common patterns")
async def analyze_patterns(ctx: Context, code: str) -> Dict[str, Any]:
    """Analyze code text for common patterns."""
    analyzer: CodebaseAnalyzer = ctx.request_context.lifespan_context["analyzer"]
    return await analyzer.analyze_patterns(code)

@mcp.tool(name="detect-architecture", description="Detect architectural patterns in a codebase")
async def detect_architecture(ctx: Context, path: str) -> Dict[str, Any]:
    """Detect architectural patterns in a codebase."""
    analyzer: CodebaseAnalyzer = ctx.request_context.lifespan_context["analyzer"]
    return await analyzer.detect_architecture(path)

@mcp.tool(name="health-check", description="Check server health status")
async def health_check(ctx: Context, force: bool = False) -> Dict[str, Any]:
    """Check the health status of server components."""
    health_monitor: HealthMonitor = ctx.request_context.lifespan_context["health_monitor"]
    return await health_monitor.check_health(force)

@mcp.tool(name="get-metrics", description="Get server performance metrics")
async def get_metrics(ctx: Context) -> Dict[str, Any]:
    """Get server performance metrics."""
    metrics_collector: MetricsCollector = ctx.request_context.lifespan_context["metrics_collector"]
    return await metrics_collector.get_all_metrics()
