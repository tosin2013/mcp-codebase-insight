"""Configuration management."""

from dataclasses import dataclass
from pathlib import Path

@dataclass
class ServerConfig:
    """Server configuration."""

    qdrant_url: str
    host: str
    port: int
    log_level: str
    docs_cache_dir: Path
    adr_dir: Path
    adr_template_path: Path
    kb_storage_dir: Path
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    collection_name: str = "codebase_analysis"
