"""Version information."""

__version__ = "0.1.0"
__author__ = "MCP Team"
__author_email__ = "team@mcp.dev"
__description__ = "MCP Codebase Insight Server"
__url__ = "https://github.com/modelcontextprotocol/mcp-codebase-insight"
__license__ = "MIT"

# Version components
VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION_SUFFIX = ""

# Build version tuple
VERSION_INFO = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

# Build version string
VERSION = ".".join(map(str, VERSION_INFO))
if VERSION_SUFFIX:
    VERSION += VERSION_SUFFIX
