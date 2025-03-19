from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, TypeVar, Generic
import asyncio
import json
from pathlib import Path
import pickle

from .config import ServerConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

@dataclass
class CacheEntry(Generic[T]):
    """Cache entry with value and metadata."""
    key: str
    value: T
    created_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        return (
            self.expires_at is not None
            and datetime.now() > self.expires_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata
        }

class Cache(Generic[T]):
    """Generic cache implementation."""

    def __init__(
        self,
        name: str,
        max_size: int,
        ttl: Optional[int] = None,
        storage_dir: Optional[Path] = None
    ):
        """Initialize cache."""
        self.name = name
        self.max_size = max_size
        self.ttl = ttl
        self.storage_dir = storage_dir
        
        # Initialize cache storage
        self.entries: Dict[str, CacheEntry[T]] = {}
        
        if storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()

    async def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        entry = self.entries.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired():
            await self.delete(key)
            return None
        
        return entry.value

    async def put(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Put value in cache."""
        # Create entry
        expires_at = None
        if ttl or self.ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl or self.ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        # Check size limit
        if len(self.entries) >= self.max_size:
            await self._evict_entries()
        
        # Store entry
        self.entries[key] = entry
        
        # Save to disk if enabled
        if self.storage_dir:
            await self._save_to_disk()

    async def delete(self, key: str) -> None:
        """Delete entry from cache."""
        if key in self.entries:
            del self.entries[key]
            
            if self.storage_dir:
                await self._save_to_disk()

    async def clear(self) -> None:
        """Clear all entries from cache."""
        self.entries.clear()
        
        if self.storage_dir:
            await self._save_to_disk()

    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get entry metadata."""
        entry = self.entries.get(key)
        return entry.metadata if entry else None

    async def update_metadata(
        self,
        key: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update entry metadata."""
        entry = self.entries.get(key)
        if entry:
            entry.metadata.update(metadata)
            
            if self.storage_dir:
                await self._save_to_disk()

    async def _evict_entries(self) -> None:
        """Evict entries to maintain size limit."""
        # Remove expired entries first
        expired = [
            key for key, entry in self.entries.items()
            if entry.is_expired()
        ]
        for key in expired:
            await self.delete(key)
        
        # If still over limit, remove oldest entries
        while len(self.entries) >= self.max_size:
            oldest_key = min(
                self.entries.keys(),
                key=lambda k: self.entries[k].created_at
            )
            await self.delete(oldest_key)

    def _load_from_disk(self) -> None:
        """Load cache from disk."""
        try:
            cache_file = self.storage_dir / f"{self.name}.cache"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    self.entries = pickle.load(f)
                logger.info(f"Loaded {len(self.entries)} entries from disk cache")
        except Exception as e:
            logger.error(f"Error loading cache from disk: {e}")

    async def _save_to_disk(self) -> None:
        """Save cache to disk."""
        try:
            cache_file = self.storage_dir / f"{self.name}.cache"
            with open(cache_file, 'wb') as f:
                pickle.dump(self.entries, f)
        except Exception as e:
            logger.error(f"Error saving cache to disk: {e}")

class CacheManager:
    """Manages multiple caches."""

    def __init__(self, config: ServerConfig):
        """Initialize cache manager."""
        self.config = config
        self.storage_dir = config.kb_storage_dir / "cache"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize caches
        self.embedding_cache = Cache[List[float]](
            name="embeddings",
            max_size=config.cache_size,
            ttl=config.cache_ttl,
            storage_dir=self.storage_dir
        )
        
        self.result_cache = Cache[Dict[str, Any]](
            name="results",
            max_size=config.cache_size,
            ttl=config.cache_ttl,
            storage_dir=self.storage_dir
        )
        
        self.doc_cache = Cache[str](
            name="docs",
            max_size=config.cache_size,
            ttl=86400,  # 24 hours
            storage_dir=self.storage_dir
        )
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())

    async def clear_all(self) -> None:
        """Clear all caches."""
        await self.embedding_cache.clear()
        await self.result_cache.clear()
        await self.doc_cache.clear()

    async def _cleanup_expired(self) -> None:
        """Cleanup expired entries periodically."""
        while True:
            try:
                # Clean up each cache
                await self._cleanup_cache(self.embedding_cache)
                await self._cleanup_cache(self.result_cache)
                await self._cleanup_cache(self.doc_cache)
                
                # Wait before next cleanup
                await asyncio.sleep(3600)  # Run hourly
                
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_cache(self, cache: Cache) -> None:
        """Cleanup expired entries in cache."""
        expired = [
            key for key, entry in cache.entries.items()
            if entry.is_expired()
        ]
        for key in expired:
            await cache.delete(key)

    async def stop(self) -> None:
        """Stop cache manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
