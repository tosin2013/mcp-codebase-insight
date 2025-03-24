from setuptools import setup, find_packages

setup(
    name="mcp-codebase-insight",
    version="0.2.0",
    description="Model Context Protocol (MCP) server for codebase analysis and insights",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Model Context Protocol",
    author_email="info@modelcontextprotocol.org",
    url="https://github.com/modelcontextprotocol/mcp-codebase-insight",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.103.2",
        "uvicorn>=0.23.2",
        "pydantic>=2.4.2",
        "qdrant-client>=1.13.3",
        "sentence-transformers>=2.2.2",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.5",
        "beautifulsoup4>=4.12.2",
        "numpy>=1.24.3",
        "scikit-learn>=1.3.0",
        "pytest>=7.4.2",
        "black>=23.9.1",
        "flake8>=6.1.0",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "mcp-codebase-insight=mcp_codebase_insight.server:run",
        ],
    },
)