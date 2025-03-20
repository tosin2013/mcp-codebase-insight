"""Cache management module."""

import json
import os
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union

class MemoryCache:
    """In-memory LRU cache."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize memory cache."""
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None
            
        # Move to end (most recently used)
        value = self.cache.pop(key)
        self.cache[key] = value
        return value
    
    def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
        if key in self.cache:
            # Move to end
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Remove oldest
            self.cache.popitem(last=False)
            
        self.cache[key] = value
    
    def remove(self, key: str) -> None:
        """Remove value from cache."""
        if key in self.cache:
            self.cache.pop(key)
    
    def clear(self) -> None:
        """Clear all values from cache."""
        self.cache.clear()

class DiskCache:
    """Disk-based cache."""
    
    def __init__(
        self,
        cache_dir: Union[str, Path],
        max_age_days: int = 7
    ):
        """Initialize disk cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age = timedelta(days=max_age_days)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
            
        # Check if expired
        if self._is_expired(cache_path):
            cache_path.unlink()
            return None
            
        try:
            with open(cache_path) as f:
                data = json.load(f)
                return data["value"]
        except Exception:
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, "w") as f:
                json.dump({
                    "value": value,
                    "timestamp": datetime.utcnow().isoformat()
                }, f)
        except Exception:
            # Ignore write errors
            pass
    
    def remove(self, key: str) -> None:
        """Remove value from cache."""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def clear(self) -> None:
        """Clear all values from cache."""
        for path in self.cache_dir.glob("*.json"):
            path.unlink()
    
    def cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        for path in self.cache_dir.glob("*.json"):
            if self._is_expired(path):
                path.unlink()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        # Use hash of key as filename
        filename = f"{hash(key)}.json"
        return self.cache_dir / filename
    
    def _is_expired(self, path: Path) -> bool:
        """Check if cache entry is expired."""
        try:
            with open(path) as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data["timestamp"])
                return datetime.utcnow() - timestamp > self.max_age
        except Exception:
            return True

class CacheManager:
    """Manager for memory and disk caching."""
    
    def __init__(self, config):
        """Initialize cache manager."""
        self.config = config
        self.enabled = config.cache_enabled
        
        if self.enabled:
            self.memory_cache = MemoryCache(
                max_size=config.memory_cache_size
            )
            
            if config.disk_cache_dir:
                self.disk_cache = DiskCache(
                    cache_dir=config.disk_cache_dir
                )
            else:
                self.disk_cache = None
    
    def get_from_memory(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        if not self.enabled:
            return None
        return self.memory_cache.get(key)
    
    def put_in_memory(self, key: str, value: Any) -> None:
        """Put value in memory cache."""
        if not self.enabled:
            return
        self.memory_cache.put(key, value)
    
    def get_from_disk(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        if not self.enabled or not self.disk_cache:
            return None
        return self.disk_cache.get(key)
    
    def put_in_disk(self, key: str, value: Any) -> None:
        """Put value in disk cache."""
        if not self.enabled or not self.disk_cache:
            return
        self.disk_cache.put(key, value)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (memory first, then disk)."""
        if not self.enabled:
            return None
            
        # Try memory cache first
        value = self.get_from_memory(key)
        if value is not None:
            return value
            
        # Try disk cache
        if self.disk_cache:
            value = self.get_from_disk(key)
            if value is not None:
                # Cache in memory for next time
                self.put_in_memory(key, value)
            return value
            
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Put value in cache (both memory and disk)."""
        if not self.enabled:
            return
            
        self.put_in_memory(key, value)
        if self.disk_cache:
            self.put_in_disk(key, value)
    
    def remove(self, key: str) -> None:
        """Remove value from cache."""
        if not self.enabled:
            return
            
        self.memory_cache.remove(key)
        if self.disk_cache:
            self.disk_cache.remove(key)
    
    def clear(self) -> None:
        """Clear all values from cache."""
        if not self.enabled:
            return
            
        self.memory_cache.clear()
        if self.disk_cache:
            self.disk_cache.clear()
    
    def cleanup(self) -> None:
        """Clean up expired cache entries."""
        if not self.enabled:
            return
            
        if self.disk_cache:
            self.disk_cache.cleanup_expired()
