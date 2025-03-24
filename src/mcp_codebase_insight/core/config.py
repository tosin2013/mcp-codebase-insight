"""Server configuration module."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class ServerConfig:
    """Server configuration."""
    
    host: str = "127.0.0.1"
    port: int = 3000
    log_level: str = "INFO"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    docs_cache_dir: Path = Path("docs")
    adr_dir: Path = Path("docs/adrs")
    kb_storage_dir: Path = Path("knowledge")
    embedding_model: str = "all-MiniLM-L6-v2"
    collection_name: str = "codebase_patterns"
    debug_mode: bool = False
    metrics_enabled: bool = True
    cache_enabled: bool = True
    memory_cache_size: int = 1000
    disk_cache_dir: Optional[Path] = Path("cache")  # Default to "cache" instead of None
    _state: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Convert string paths to Path objects and process defaults."""
        # Convert string paths to Path objects
        for attr_name in ["docs_cache_dir", "adr_dir", "kb_storage_dir"]:
            attr_value = getattr(self, attr_name)
            if attr_value is not None and not isinstance(attr_value, Path):
                setattr(self, attr_name, Path(attr_value))

        # Handle disk_cache_dir specifically
        if self.cache_enabled:
            if self.disk_cache_dir is None:
                # Default to "cache" directory when None but cache is enabled
                self.disk_cache_dir = Path("cache")
                logger.debug(f"Setting default disk_cache_dir to {self.disk_cache_dir}")
            elif not isinstance(self.disk_cache_dir, Path):
                self.disk_cache_dir = Path(self.disk_cache_dir)
        else:
            # If cache is disabled, set disk_cache_dir to None regardless of previous value
            self.disk_cache_dir = None
            logger.debug("Cache disabled, setting disk_cache_dir to None")
        
        # Initialize state
        self._state = {
            "initialized": False,
            "components": {},
            "metrics": {},
            "errors": []
        }
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Create configuration from environment variables."""
        cache_enabled = os.getenv("MCP_CACHE_ENABLED", "true").lower() == "true"
        disk_cache_path = os.getenv("MCP_DISK_CACHE_DIR", "cache")
        
        return cls(
            host=os.getenv("MCP_HOST", "127.0.0.1"),
            port=int(os.getenv("MCP_PORT", "3000")),
            log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            embedding_model=os.getenv("MCP_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            collection_name=os.getenv("MCP_COLLECTION_NAME", "codebase_patterns"),
            docs_cache_dir=Path(os.getenv("MCP_DOCS_CACHE_DIR", "docs")),
            adr_dir=Path(os.getenv("MCP_ADR_DIR", "docs/adrs")),
            kb_storage_dir=Path(os.getenv("MCP_KB_STORAGE_DIR", "knowledge")),
            disk_cache_dir=Path(disk_cache_path) if cache_enabled else None,
            debug_mode=os.getenv("MCP_DEBUG", "false").lower() == "true",
            metrics_enabled=os.getenv("MCP_METRICS_ENABLED", "true").lower() == "true",
            cache_enabled=cache_enabled,
            memory_cache_size=int(os.getenv("MCP_MEMORY_CACHE_SIZE", "1000"))
        )
    
    def create_directories(self) -> None:
        """Create all required directories for the server.
        
        This method should be called during server initialization to ensure
        all necessary directories exist before components are initialized.
        """
        logger.debug("Creating required directories")
        
        # Create standard directories
        self.docs_cache_dir.mkdir(parents=True, exist_ok=True)
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        self.kb_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create cache directory if enabled and configured
        if self.cache_enabled and self.disk_cache_dir is not None:
            logger.debug(f"Creating disk cache directory: {self.disk_cache_dir}")
            self.disk_cache_dir.mkdir(parents=True, exist_ok=True)
        elif not self.cache_enabled:
            logger.debug("Cache is disabled, skipping disk cache directory creation")
        
        logger.debug("All required directories created")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value."""
        return self._state.get(key, default)
    
    def set_state(self, key: str, value: Any):
        """Set state value."""
        self._state[key] = value
    
    def update_state(self, updates: Dict[str, Any]):
        """Update multiple state values."""
        self._state.update(updates)
    
    def clear_state(self):
        """Clear all state."""
        self._state.clear()
        self._state = {
            "initialized": False,
            "components": {},
            "metrics": {},
            "errors": []
        }
