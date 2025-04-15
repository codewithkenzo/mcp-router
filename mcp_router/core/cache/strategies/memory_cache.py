"""
Memory Cache Module

This module provides an in-memory cache implementation for the MCP Router system.
"""

import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set, TypeVar, Generic, Callable
from collections import OrderedDict

from mcp_router.core.cache.cache_interface import CacheInterface, CacheEntry

logger = logging.getLogger(__name__)

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

class MemoryCache(CacheInterface[K, V]):
    """
    In-memory cache implementation.
    
    This cache stores values in memory with optional expiration.
    """
    
    def __init__(self, max_size: int = 1000, cleanup_interval: int = 60):
        """
        Initialize the memory cache.
        
        Args:
            max_size: Maximum number of entries in the cache
            cleanup_interval: Interval in seconds for cleaning up expired entries
        """
        self.cache: Dict[K, CacheEntry[V]] = OrderedDict()
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self.cleanup_task = None
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.created_at = time.time()
    
    async def start_cleanup_task(self) -> None:
        """
        Start the cleanup task.
        """
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup_task(self) -> None:
        """
        Stop the cleanup task.
        """
        if self.cleanup_task is not None:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            self.cleanup_task = None
    
    async def _cleanup_loop(self) -> None:
        """
        Periodically clean up expired entries.
        """
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired()
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
            raise
    
    async def _cleanup_expired(self) -> None:
        """
        Clean up expired entries.
        """
        # Find expired entries using list comprehension
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        
        # Delete expired entries
        for key in expired_keys:
            del self.cache[key]
            self.expirations += 1
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
    
    async def get(self, key: K) -> Optional[V]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        entry = self.cache.get(key)
        
        if entry is None:
            self.misses += 1
            return None
        
        if entry.is_expired():
            # Remove expired entry
            await self.delete(key)
            self.misses += 1
            self.expirations += 1
            return None
        
        # Move entry to the end (most recently used)
        self.cache.move_to_end(key)
        
        # Update access metadata
        entry.access()
        
        self.hits += 1
        return entry.value
    
    async def set(self, key: K, value: V, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        # Check if cache is full and needs eviction
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Evict least recently used entry
            self.cache.popitem(last=False)
            self.evictions += 1
        
        # Create new entry
        entry = CacheEntry(value, ttl)
        
        # Add to cache
        self.cache[key] = entry
        
        # Move to the end (most recently used)
        self.cache.move_to_end(key)
        
        return True
    
    async def delete(self, key: K) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    async def exists(self, key: K) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key exists, False otherwise
        """
        if key not in self.cache:
            return False
        
        entry = self.cache[key]
        if entry.is_expired():
            # Remove expired entry
            await self.delete(key)
            return False
        
        return True
    
    async def clear(self) -> bool:
        """
        Clear the cache.
        
        Returns:
            True if successful, False otherwise
        """
        self.cache.clear()
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "type": "memory",
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "uptime": time.time() - self.created_at
        }
