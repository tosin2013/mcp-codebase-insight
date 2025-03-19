from dataclasses import dataclass
from typing import Optional, List
import os
from pathlib import Path
from dotenv import load_dotenv

from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ServerConfig:
    """Configuration settings for the MCP server."""
    
    # Qdrant settings
    qdrant_url: str
    qdrant_timeout: int = 30
    max_retries: int = 3
    collection_name: str = "codebase_analysis"
    
    # Embedding settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 32
    
    # Cache settings
    cache_enabled: bool = True
    cache_size: int = 1000
    cache_ttl: int = 3600  # 1 hour
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 3000
    log_level: str = "INFO"
    
    # Documentation settings
    docs_cache_dir: Path = Path("references")
    docs_refresh_interval: int = 86400  # 24 hours
    docs_max_size: int = 1000000  # 1MB per file
    gitignore_path: Path = Path(".gitignore")
    
    # ADR settings
    adr_dir: Path = Path("docs/adrs")
    adr_template_path: Path = Path("docs/templates/adr.md")
    adr_index_path: Path = Path("docs/adrs/index.md")
    
    # Debug settings
    debug_log_dir: Path = Path("logs/debug")
    debug_history_size: int = 100
    debug_retention_days: int = 30
    
    # Analysis settings
    analysis_timeout: int = 300  # 5 minutes
    max_file_size: int = 10000000  # 10MB
    excluded_patterns: List[str] = None
    
    # Knowledge base settings
    kb_storage_dir: Path = Path("knowledge")
    kb_backup_interval: int = 86400  # 24 hours
    kb_max_patterns: int = 10000
    
    def __post_init__(self):
        """Initialize default lists."""
        if self.excluded_patterns is None:
            self.excluded_patterns = [
                "*.pyc",
                "__pycache__",
                "*.git*",
                "*.env*",
                "node_modules",
                "venv",
                ".venv"
            ]
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create config from environment variables."""
        load_dotenv()
        
        config = cls(
            # Qdrant settings
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            qdrant_timeout=int(os.getenv("QDRANT_TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            collection_name=os.getenv("COLLECTION_NAME", "codebase_analysis"),
            
            # Embedding settings
            embedding_model=os.getenv(
                "EMBEDDING_MODEL", 
                "sentence-transformers/all-MiniLM-L6-v2"
            ),
            embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
            
            # Cache settings
            cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            cache_size=int(os.getenv("CACHE_SIZE", "1000")),
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
            
            # Server settings
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "3000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            
            # Documentation settings
            docs_cache_dir=Path(os.getenv("DOCS_CACHE_DIR", "references")),
            docs_refresh_interval=int(os.getenv("DOCS_REFRESH_INTERVAL", "86400")),
            docs_max_size=int(os.getenv("DOCS_MAX_SIZE", "1000000")),
            gitignore_path=Path(os.getenv("GITIGNORE_PATH", ".gitignore")),
            
            # ADR settings
            adr_dir=Path(os.getenv("ADR_DIR", "docs/adrs")),
            adr_template_path=Path(os.getenv("ADR_TEMPLATE_PATH", "docs/templates/adr.md")),
            adr_index_path=Path(os.getenv("ADR_INDEX_PATH", "docs/adrs/index.md")),
            
            # Debug settings
            debug_log_dir=Path(os.getenv("DEBUG_LOG_DIR", "logs/debug")),
            debug_history_size=int(os.getenv("DEBUG_HISTORY_SIZE", "100")),
            debug_retention_days=int(os.getenv("DEBUG_RETENTION_DAYS", "30")),
            
            # Analysis settings
            analysis_timeout=int(os.getenv("ANALYSIS_TIMEOUT", "300")),
            max_file_size=int(os.getenv("MAX_FILE_SIZE", "10000000")),
            excluded_patterns=os.getenv("EXCLUDED_PATTERNS", "").split(",") if os.getenv("EXCLUDED_PATTERNS") else None,
            
            # Knowledge base settings
            kb_storage_dir=Path(os.getenv("KB_STORAGE_DIR", "knowledge")),
            kb_backup_interval=int(os.getenv("KB_BACKUP_INTERVAL", "86400")),
            kb_max_patterns=int(os.getenv("KB_MAX_PATTERNS", "10000"))
        )
        
        logger.info(f"Loaded configuration: {config}")
        return config
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "qdrant": {
                "url": self.qdrant_url,
                "timeout": self.qdrant_timeout,
                "max_retries": self.max_retries,
                "collection_name": self.collection_name
            },
            "embedding": {
                "model": self.embedding_model,
                "batch_size": self.embedding_batch_size
            },
            "cache": {
                "enabled": self.cache_enabled,
                "size": self.cache_size,
                "ttl": self.cache_ttl
            },
            "server": {
                "host": self.host,
                "port": self.port,
                "log_level": self.log_level
            },
            "documentation": {
                "cache_dir": str(self.docs_cache_dir),
                "refresh_interval": self.docs_refresh_interval,
                "max_size": self.docs_max_size,
                "gitignore_path": str(self.gitignore_path)
            },
            "adr": {
                "dir": str(self.adr_dir),
                "template_path": str(self.adr_template_path),
                "index_path": str(self.adr_index_path)
            },
            "debug": {
                "log_dir": str(self.debug_log_dir),
                "history_size": self.debug_history_size,
                "retention_days": self.debug_retention_days
            },
            "analysis": {
                "timeout": self.analysis_timeout,
                "max_file_size": self.max_file_size,
                "excluded_patterns": self.excluded_patterns
            },
            "knowledge_base": {
                "storage_dir": str(self.kb_storage_dir),
                "backup_interval": self.kb_backup_interval,
                "max_patterns": self.kb_max_patterns
            }
        }
