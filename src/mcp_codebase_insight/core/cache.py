"""Cache management module."""

import json
import os
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union
import logging

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
        self.memory_cache = None
        self.disk_cache = None
        self.initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize cache components."""
        if self.initialized:
            self.logger.debug("Cache manager already initialized")
            return
            
        try:
            self.logger.debug(f"Initializing cache manager (enabled: {self.enabled})")
            
            if self.enabled:
                self.logger.debug(f"Creating memory cache with size: {self.config.memory_cache_size}")
                self.memory_cache = MemoryCache(
                    max_size=self.config.memory_cache_size
                )
                
                # Check if disk cache is configured and enabled
                if self.config.disk_cache_dir is not None:
                    self.logger.debug(f"Creating disk cache at: {self.config.disk_cache_dir}")
                    
                    # Ensure directory exists (should be created by ServerConfig.create_directories)
                    if not self.config.disk_cache_dir.exists():
                        self.logger.debug(f"Creating disk cache directory: {self.config.disk_cache_dir}")
                        self.config.disk_cache_dir.mkdir(parents=True, exist_ok=True)
                    
                    self.disk_cache = DiskCache(
                        cache_dir=self.config.disk_cache_dir
                    )
                else:
                    self.logger.debug("Disk cache directory not configured, skipping disk cache")
            else:
                self.logger.debug("Cache is disabled, not initializing memory or disk cache")
            
            self.initialized = True
            self.logger.debug("Cache manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing cache manager: {e}")
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize cache manager: {str(e)}")

    def get_from_memory(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        if not self.enabled or not self.memory_cache:
            return None
        return self.memory_cache.get(key)
    
    def put_in_memory(self, key: str, value: Any) -> None:
        """Put value in memory cache."""
        if not self.enabled or not self.memory_cache:
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
            
        if self.memory_cache:
            self.memory_cache.remove(key)
        if self.disk_cache:
            self.disk_cache.remove(key)
    
    def clear(self) -> None:
        """Clear all values from cache."""
        if not self.enabled:
            return
            
        if self.memory_cache:
            self.memory_cache.clear()
        if self.disk_cache:
            self.disk_cache.clear()
    
    async def cleanup(self) -> None:
        """Clean up expired cache entries and clear memory cache."""
        if not self.initialized:
            return
            
        try:
            if not self.enabled:
                return
                
            # Clear memory cache
            if self.memory_cache:
                self.memory_cache.clear()
                
            # Clean up disk cache
            if self.disk_cache:
                self.disk_cache.cleanup_expired()
        except Exception as e:
            print(f"Error cleaning up cache manager: {e}")
        finally:
            self.initialized = False

    async def clear_all(self) -> None:
        """Clear all values from cache asynchronously."""
        self.clear()
