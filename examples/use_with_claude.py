"""Example of using MCP Codebase Insight with Claude."""

import json
import httpx
import os
from typing import Dict, Any
import asyncio

# Configure server URL
SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000")

async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call a tool endpoint on the server."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVER_URL}/tools/{name}",
            json={
                "name": name,
                "arguments": arguments
            }
        )
        response.raise_for_status()
        return response.json()

async def analyze_code(code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Analyze code using the server."""
    return await call_tool("analyze-code", {
        "code": code,
        "context": context or {}
    })

async def search_knowledge(query: str, pattern_type: str = None) -> Dict[str, Any]:
    """Search knowledge base."""
    return await call_tool("search-knowledge", {
        "query": query,
        "type": pattern_type,
        "limit": 5
    })

async def create_adr(
    title: str,
    context: Dict[str, Any],
    options: list,
    decision: str
) -> Dict[str, Any]:
    """Create an ADR."""
    return await call_tool("create-adr", {
        "title": title,
        "context": context,
        "options": options,
        "decision": decision
    })

async def debug_issue(
    description: str,
    issue_type: str = None,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Debug an issue."""
    return await call_tool("debug-issue", {
        "description": description,
        "type": issue_type,
        "context": context or {}
    })

async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status and results."""
    return await call_tool("get-task", {
        "task_id": task_id
    })

async def main():
    """Example usage."""
    try:
        # Example code analysis
        code = """
def calculate_fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
        """
        print("\nAnalyzing code...")
        result = await analyze_code(code)
        print(json.dumps(result, indent=2))

        # Example knowledge search
        print("\nSearching knowledge base...")
        result = await search_knowledge(
            query="What are the best practices for error handling in Python?",
            pattern_type="code"
        )
        print(json.dumps(result, indent=2))

        # Example ADR creation
        print("\nCreating ADR...")
        result = await create_adr(
            title="Use FastAPI for REST API",
            context={
                "problem": "Need a modern Python web framework",
                "constraints": ["Must be async", "Must have good documentation"]
            },
            options=[
                {
                    "title": "FastAPI",
                    "pros": ["Async by default", "Great docs", "Type hints"],
                    "cons": ["Newer framework"]
                },
                {
                    "title": "Flask",
                    "pros": ["Mature", "Simple"],
                    "cons": ["Not async by default"]
                }
            ],
            decision="We will use FastAPI for its async support and type hints"
        )
        print(json.dumps(result, indent=2))

        # Example debugging
        print("\nDebugging issue...")
        result = await debug_issue(
            description="Application crashes when processing large files",
            issue_type="performance",
            context={
                "file_size": "2GB",
                "memory_usage": "8GB",
                "error": "MemoryError"
            }
        )
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
