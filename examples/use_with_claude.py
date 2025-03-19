#!/usr/bin/env python3
"""Example of using the MCP server with Claude."""

import asyncio
import json
from typing import Dict, Any, List
import aiohttp
import click

async def analyze_code(code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Analyze code using MCP server."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:3000/tools/analyze-code",
            json={
                "code": code,
                "context": context or {}
            }
        ) as response:
            return await response.json()

async def create_adr(
    title: str,
    context: Dict[str, str],
    options: List[Dict],
    decision: str
) -> Dict[str, Any]:
    """Create ADR using MCP server."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:3000/tools/create-adr",
            json={
                "title": title,
                "context": context,
                "options": options,
                "decision": decision
            }
        ) as response:
            return await response.json()

async def debug_issue(
    description: str,
    type: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Debug issue using MCP server."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:3000/tools/debug-issue",
            json={
                "description": description,
                "type": type,
                "context": context
            }
        ) as response:
            return await response.json()

async def search_knowledge(
    query: str,
    type: str = None,
    limit: int = 5
) -> Dict[str, Any]:
    """Search knowledge base using MCP server."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:3000/tools/search-knowledge",
            json={
                "query": query,
                "type": type,
                "limit": limit
            }
        ) as response:
            return await response.json()

async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status from MCP server."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://localhost:3000/tools/get-task?task_id={task_id}"
        ) as response:
            return await response.json()

async def example_code_analysis():
    """Example of code analysis workflow."""
    # Example code to analyze
    code = """
def process_data(data):
    results = []
    for item in data:
        if item.get('active'):
            value = item.get('value', 0)
            if value > 100:
                results.append(value * 2)
    return results
    """
    
    print("\n=== Code Analysis Example ===")
    print("Analyzing code...")
    
    # Analyze code
    result = await analyze_code(
        code,
        context={
            "language": "python",
            "purpose": "data processing"
        }
    )
    
    # Get task results
    task_result = await get_task_status(result["task_id"])
    
    print("\nAnalysis Results:")
    for step in task_result["steps"]:
        if step["result"]:
            print(f"\n{step['description']}:")
            print(step["result"])

async def example_adr_creation():
    """Example of ADR creation workflow."""
    print("\n=== ADR Creation Example ===")
    print("Creating ADR...")
    
    # Create ADR
    result = await create_adr(
        title="Use FastAPI for REST API",
        context={
            "technical": "Building a new REST API service",
            "business": "Need high performance and good developer experience"
        },
        options=[
            {
                "name": "FastAPI",
                "description": "Modern, fast Python web framework",
                "pros": ["Fast", "Good docs", "Type hints"],
                "cons": ["Newer framework", "Smaller community"]
            },
            {
                "name": "Flask",
                "description": "Lightweight Python web framework",
                "pros": ["Simple", "Mature", "Large community"],
                "cons": ["Slower", "Manual type checking"]
            }
        ],
        decision="FastAPI chosen for performance and developer experience"
    )
    
    # Get task results
    task_result = await get_task_status(result["task_id"])
    
    print("\nADR Creation Results:")
    print(f"ADR created at: {result.get('adr_path')}")
    for step in task_result["steps"]:
        if step["result"]:
            print(f"\n{step['description']}:")
            print(step["result"])

async def example_debugging():
    """Example of debugging workflow."""
    print("\n=== Debugging Example ===")
    print("Starting debug session...")
    
    # Debug issue
    result = await debug_issue(
        description="Memory leak in data processing service",
        type="performance",
        context={
            "symptoms": "Memory usage grows over time",
            "environment": "Production server",
            "impact": "High",
            "logs": "Memory usage increases 5% per hour"
        }
    )
    
    # Get task results
    task_result = await get_task_status(result["task_id"])
    
    print("\nDebugging Results:")
    for step in task_result["steps"]:
        if step["result"]:
            print(f"\n{step['description']}:")
            print(step["result"])

async def example_knowledge_search():
    """Example of knowledge base search."""
    print("\n=== Knowledge Search Example ===")
    print("Searching knowledge base...")
    
    # Search patterns
    result = await search_knowledge(
        query="python error handling best practices",
        type="best_practice",
        limit=3
    )
    
    print("\nSearch Results:")
    for pattern in result["patterns"]:
        print(f"\n{pattern['name']} (Score: {pattern['similarity']:.2f}):")
        print(f"Type: {pattern['type']}")
        print(f"Description: {pattern['description']}")

@click.command()
@click.option(
    "--example",
    type=click.Choice(["all", "analysis", "adr", "debug", "search"]),
    default="all",
    help="Example to run"
)
def main(example: str):
    """Run MCP server examples."""
    async def run():
        if example in ["all", "analysis"]:
            await example_code_analysis()
        
        if example in ["all", "adr"]:
            await example_adr_creation()
        
        if example in ["all", "debug"]:
            await example_debugging()
        
        if example in ["all", "search"]:
            await example_knowledge_search()
    
    asyncio.run(run())

if __name__ == "__main__":
    main()
