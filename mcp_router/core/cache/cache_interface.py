"""
Cache Interface Module

This module defines the interface for caches in the MCP Router system.
"""

import abc
import time
from typing import Dict, List, Any, Optional, Tuple, Set, TypeVar, Generic, Callable

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

class CacheInterface(Generic[K, V], abc.ABC):
    """
    Base interface for all MCP Router caches.
    
    Caches must implement this interface to be used by the cache manager.
    """
    
    @abc.abstractmethod
    async def get(self, key: K) -> Optional[V]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
    async def delete(self, key: K) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def exists(self, key: K) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key exists, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def clear(self) -> bool:
        """
        Clear the cache.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        pass

class CacheEntry(Generic[V]):
    """
    Cache entry with metadata.
    
    This class represents a cached value with metadata such as
    creation time, expiration time, and access count.
    """
    
    def __init__(self, value: V, ttl: Optional[int] = None):
        """
        Initialize a cache entry.
        
        Args:
            value: Value to cache
            ttl: Optional time-to-live in seconds
        """
        self.value = value
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl if ttl is not None else None
        self.last_accessed_at = self.created_at
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """
        Check if the cache entry is expired.
        
        Returns:
            True if expired, False otherwise
        """
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def access(self) -> None:
        """
        Mark the cache entry as accessed.
        """
        self.last_accessed_at = time.time()
        self.access_count += 1
