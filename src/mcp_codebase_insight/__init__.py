"""MCP server for intelligent codebase analysis."""

from mcp_codebase_insight.version import __version__
from mcp_codebase_insight.server import CodebaseAnalysisServer

__all__ = ["CodebaseAnalysisServer", "__version__"]
