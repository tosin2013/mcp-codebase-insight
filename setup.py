from setuptools import setup, find_packages
import re
import os

# Read version from __init__.py
with open(os.path.join("src", "mcp_codebase_insight", "__init__.py"), "r") as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string")

setup(
    name="mcp-codebase-insight",
    version=version,
    description="Model Context Protocol (MCP) server for codebase analysis and insights",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Model Context Protocol",
    author_email="info@modelcontextprotocol.org",
    url="https://github.com/tosin2013/mcp-codebase-insight",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.103.2,<0.104.0",
        "uvicorn>=0.23.2,<0.24.0",
        "pydantic>=2.4.2,<3.0.0",
        "starlette>=0.27.0,<0.28.0",
        "asyncio>=3.4.3",
        "aiohttp>=3.9.0,<4.0.0",
        "qdrant-client>=1.13.3",
        "sentence-transformers>=2.2.2",
        "torch>=2.0.0",
        "transformers>=4.34.0,<5.0.0",
        "python-frontmatter>=1.0.0",
        "markdown>=3.4.4",
        "PyYAML>=6.0.1",
        "structlog>=23.1.0",
        "psutil>=5.9.5",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "scipy>=1.11.0",
        "numpy>=1.24.0",
        "python-slugify>=8.0.0",
        "slugify>=0.0.1",
        "uvx>=0.4.0",
        "mcp-server-qdrant>=0.2.0",
        "mcp>=1.5.0,<1.6.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "mcp-codebase-insight=mcp_codebase_insight.server:run",
        ],
    },
)