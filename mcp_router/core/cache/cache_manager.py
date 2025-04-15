"""
Cache Manager Module

This module provides a cache manager for the MCP Router system,
allowing for efficient caching of data with different strategies.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set, TypeVar, Generic, Callable, Type

from mcp_router.core.cache.cache_interface import CacheInterface
from mcp_router.core.cache.strategies.memory_cache import MemoryCache
from mcp_router.core.cache.strategies.disk_cache import DiskCache

logger = logging.getLogger(__name__)

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

class CacheManager:
    """
    Manager for MCP Router caches.
    
    This class provides a unified interface for different cache implementations,
    with support for multi-level caching and cache invalidation.
    """
    
    def __init__(self, 
                 memory_cache_size: int = 1000, 
                 disk_cache_size: int = 10000,
                 disk_cache_dir: Optional[str] = None,
                 use_disk_cache: bool = True):
        """
        Initialize the cache manager.
        
        Args:
            memory_cache_size: Maximum number of entries in the memory cache
            disk_cache_size: Maximum number of entries in the disk cache
            disk_cache_dir: Directory to store disk cache files
            use_disk_cache: Whether to use disk caching
        """
        # Create memory cache
        self.memory_cache = MemoryCache(max_size=memory_cache_size)
        
        # Create disk cache if enabled
        self.disk_cache = None
        if use_disk_cache:
            self.disk_cache = DiskCache(
                cache_dir=disk_cache_dir,
                max_size=disk_cache_size
            )
        
        # Dictionary of cache keys to invalidation tags
        self.invalidation_tags: Dict[str, Set[str]] = {}
        
        # Dictionary of invalidation tags to cache keys
        self.tag_to_keys: Dict[str, Set[str]] = {}
    
    async def initialize(self) -> None:
        """
        Initialize the cache manager.
        """
        logger.info("Initializing cache manager...")
        
        # Start cleanup tasks
        await self.memory_cache.start_cleanup_task()
        
        if self.disk_cache:
            await self.disk_cache.start_cleanup_task()
    
    async def shutdown(self) -> None:
        """
        Shutdown the cache manager.
        """
        logger.info("Shutting down cache manager...")
        
        # Stop cleanup tasks
        await self.memory_cache.stop_cleanup_task()
        
        if self.disk_cache:
            await self.disk_cache.stop_cleanup_task()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        # Try memory cache first
        value = await self.memory_cache.get(key)
        if value is not None:
            return value
        
        # Try disk cache if enabled
        if self.disk_cache:
            value = await self.disk_cache.get(key)
            if value is not None:
                # Store in memory cache for faster access next time
                await self.memory_cache.set(key, value)
                return value
        
        return None
    
    async def set(self, 
                 key: str, 
                 value: Any, 
                 ttl: Optional[int] = None, 
                 tags: Optional[List[str]] = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional time-to-live in seconds
            tags: Optional list of invalidation tags
            
        Returns:
            True if successful, False otherwise
        """
        # Store in memory cache
        memory_result = await self.memory_cache.set(key, value, ttl)
        
        # Store in disk cache if enabled
        disk_result = True
        if self.disk_cache:
            disk_result = await self.disk_cache.set(key, value, ttl)
        
        # Store invalidation tags
        if tags:
            self._add_tags(key, tags)
        
        return memory_result and disk_result
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        # Delete from memory cache
        memory_result = await self.memory_cache.delete(key)
        
        # Delete from disk cache if enabled
        disk_result = True
        if self.disk_cache:
            disk_result = await self.disk_cache.delete(key)
        
        # Remove invalidation tags
        self._remove_key(key)
        
        return memory_result and disk_result
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key exists, False otherwise
        """
        # Check memory cache first
        if await self.memory_cache.exists(key):
            return True
        
        # Check disk cache if enabled
        if self.disk_cache and await self.disk_cache.exists(key):
            return True
        
        return False
    
    async def clear(self) -> bool:
        """
        Clear the cache.
        
        Returns:
            True if successful, False otherwise
        """
        # Clear memory cache
        memory_result = await self.memory_cache.clear()
        
        # Clear disk cache if enabled
        disk_result = True
        if self.disk_cache:
            disk_result = await self.disk_cache.clear()
        
        # Clear invalidation tags
        self.invalidation_tags.clear()
        self.tag_to_keys.clear()
        
        return memory_result and disk_result
    
    async def invalidate_tag(self, tag: str) -> int:
        """
        Invalidate all cache entries with a specific tag.
        
        Args:
            tag: Invalidation tag
            
        Returns:
            Number of invalidated entries
        """
        if tag not in self.tag_to_keys:
            return 0
        
        # Get keys with this tag
        keys = self.tag_to_keys[tag].copy()
        
        # Delete each key
        count = 0
        for key in keys:
            if await self.delete(key):
                count += 1
        
        # Remove tag
        if tag in self.tag_to_keys:
            del self.tag_to_keys[tag]
        
        return count
    
    async def invalidate_tags(self, tags: List[str]) -> int:
        """
        Invalidate all cache entries with any of the specified tags.
        
        Args:
            tags: List of invalidation tags
            
        Returns:
            Number of invalidated entries
        """
        # Get all keys with these tags
        keys = set()
        for tag in tags:
            if tag in self.tag_to_keys:
                keys.update(self.tag_to_keys[tag])
        
        # Delete each key
        count = 0
        for key in keys:
            if await self.delete(key):
                count += 1
        
        # Remove tags
        for tag in tags:
            if tag in self.tag_to_keys:
                del self.tag_to_keys[tag]
        
        return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        stats = {
            "memory_cache": await self.memory_cache.get_stats()
        }
        
        if self.disk_cache:
            stats["disk_cache"] = await self.disk_cache.get_stats()
        
        stats["invalidation_tags"] = len(self.tag_to_keys)
        stats["tagged_keys"] = len(self.invalidation_tags)
        
        return stats
    
    def _add_tags(self, key: str, tags: List[str]) -> None:
        """
        Add invalidation tags to a cache key.
        
        Args:
            key: Cache key
            tags: List of invalidation tags
        """
        # Add tags to key
        if key not in self.invalidation_tags:
            self.invalidation_tags[key] = set()
        
        self.invalidation_tags[key].update(tags)
        
        # Add key to tags
        for tag in tags:
            if tag not in self.tag_to_keys:
                self.tag_to_keys[tag] = set()
            
            self.tag_to_keys[tag].add(key)
    
    def _remove_key(self, key: str) -> None:
        """
        Remove a key from invalidation tags.
        
        Args:
            key: Cache key
        """
        if key not in self.invalidation_tags:
            return
        
        # Get tags for this key
        tags = self.invalidation_tags[key]
        
        # Remove key from each tag
        for tag in tags:
            if tag in self.tag_to_keys and key in self.tag_to_keys[tag]:
                self.tag_to_keys[tag].remove(key)
                
                # Remove tag if empty
                if not self.tag_to_keys[tag]:
                    del self.tag_to_keys[tag]
        
        # Remove key from invalidation tags
        del self.invalidation_tags[key]
    
    async def cached(self, 
                    func: Callable, 
                    key: str, 
                    ttl: Optional[int] = None, 
                    tags: Optional[List[str]] = None) -> Any:
        """
        Get a cached value or compute it if not in cache.
        
        Args:
            func: Function to compute the value if not in cache
            key: Cache key
            ttl: Optional time-to-live in seconds
            tags: Optional list of invalidation tags
            
        Returns:
            Cached or computed value
        """
        # Try to get from cache
        value = await self.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = await func()
        
        # Store in cache
        await self.set(key, value, ttl, tags)
        
        return value
