"""Server configuration module."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class ServerConfig:
    """Server configuration."""
    
    host: str = "127.0.0.1"
    port: int = 3000
    log_level: str = "INFO"
    qdrant_url: str = "http://localhost:6333"
    docs_cache_dir: Path = Path("docs")
    adr_dir: Path = Path("docs/adrs")
    kb_storage_dir: Path = Path("knowledge")
    embedding_model: str = "all-MiniLM-L6-v2"
    collection_name: str = "codebase_patterns"
    debug_mode: bool = False
    metrics_enabled: bool = True
    cache_enabled: bool = True
    memory_cache_size: int = 1000
    disk_cache_dir: Optional[Path] = None
    
    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.docs_cache_dir, str):
            self.docs_cache_dir = Path(self.docs_cache_dir)
        if isinstance(self.adr_dir, str):
            self.adr_dir = Path(self.adr_dir)
        if isinstance(self.kb_storage_dir, str):
            self.kb_storage_dir = Path(self.kb_storage_dir)
        if isinstance(self.disk_cache_dir, str):
            self.disk_cache_dir = Path(self.disk_cache_dir)
