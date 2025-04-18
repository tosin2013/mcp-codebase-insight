#!/usr/bin/env python3
"""
Knowledge Base Validation Script
Tests knowledge base operations using Firecrawl MCP.
"""

import asyncio
import logging
from mcp_firecrawl import (
    test_knowledge_operations,
    validate_entity_relations,
    verify_query_results
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def validate_knowledge_base(config: dict) -> bool:
    """Validate knowledge base operations."""
    logger.info("Testing knowledge base operations...")
    
    # Test basic knowledge operations
    ops_result = await test_knowledge_operations({
        "url": "http://localhost:8001",
        "auth_token": config["API_KEY"],
        "test_entities": [
            {"name": "TestClass", "type": "class"},
            {"name": "test_method", "type": "method"},
            {"name": "test_variable", "type": "variable"}
        ],
        "verify_persistence": True
    })
    
    # Validate entity relations
    relations_result = await validate_entity_relations({
        "url": "http://localhost:8001",
        "auth_token": config["API_KEY"],
        "test_relations": [
            {"from": "TestClass", "to": "test_method", "type": "contains"},
            {"from": "test_method", "to": "test_variable", "type": "uses"}
        ],
        "verify_bidirectional": True
    })
    
    # Verify query functionality
    query_result = await verify_query_results({
        "url": "http://localhost:8001",
        "auth_token": config["API_KEY"],
        "test_queries": [
            "find classes that use test_variable",
            "find methods in TestClass",
            "find variables used by test_method"
        ],
        "expected_matches": {
            "classes": ["TestClass"],
            "methods": ["test_method"],
            "variables": ["test_variable"]
        }
    })
    
    all_passed = all([
        ops_result.success,
        relations_result.success,
        query_result.success
    ])
    
    if all_passed:
        logger.info("Knowledge base validation successful")
    else:
        logger.error("Knowledge base validation failed")
        if not ops_result.success:
            logger.error("Knowledge operations failed")
        if not relations_result.success:
            logger.error("Entity relations validation failed")
        if not query_result.success:
            logger.error("Query validation failed")
    
    return all_passed

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from scripts.config import load_config
    config = load_config()
    
    success = asyncio.run(validate_knowledge_base(config))
    sys.exit(0 if success else 1) 