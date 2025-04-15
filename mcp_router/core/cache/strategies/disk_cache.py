"""
Disk Cache Module

This module provides a disk-based cache implementation for the MCP Router system.
"""

import os
import json
import time
import logging
import asyncio
import pickle
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set, TypeVar, Generic, Callable
from pathlib import Path

from mcp_router.core.cache.cache_interface import CacheInterface, CacheEntry

logger = logging.getLogger(__name__)

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

class DiskCache(CacheInterface[K, V]):
    """
    Disk-based cache implementation.
    
    This cache stores values on disk with optional expiration.
    """
    
    def __init__(self, 
                 cache_dir: Optional[str] = None, 
                 max_size: int = 10000, 
                 cleanup_interval: int = 300):
        """
        Initialize the disk cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_size: Maximum number of entries in the cache
            cleanup_interval: Interval in seconds for cleaning up expired entries
        """
        self.cache_dir = cache_dir or os.path.expanduser("~/.mcp_router/cache")
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self.cleanup_task = None
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Create metadata directory
        self.metadata_dir = os.path.join(self.cache_dir, "metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        # Create data directory
        self.data_dir = os.path.join(self.cache_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.created_at = time.time()
        
        # Load statistics if they exist
        self._load_stats()
    
    def _load_stats(self) -> None:
        """
        Load cache statistics from disk.
        """
        stats_file = os.path.join(self.cache_dir, "stats.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                
                self.hits = stats.get("hits", 0)
                self.misses = stats.get("misses", 0)
                self.evictions = stats.get("evictions", 0)
                self.expirations = stats.get("expirations", 0)
                self.created_at = stats.get("created_at", time.time())
            
            except Exception as e:
                logger.error(f"Error loading cache statistics: {e}")
    
    def _save_stats(self) -> None:
        """
        Save cache statistics to disk.
        """
        stats_file = os.path.join(self.cache_dir, "stats.json")
        try:
            stats = {
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "expirations": self.expirations,
                "created_at": self.created_at,
                "updated_at": time.time()
            }
            
            with open(stats_file, 'w') as f:
                json.dump(stats, f)
        
        except Exception as e:
            logger.error(f"Error saving cache statistics: {e}")
    
    def _get_key_hash(self, key: K) -> str:
        """
        Get a hash of a key for use in filenames.
        
        Args:
            key: Cache key
            
        Returns:
            Hash string
        """
        # Convert key to string and encode
        key_str = str(key).encode('utf-8')
        
        # Create hash
        return hashlib.md5(key_str).hexdigest()
    
    def _get_metadata_path(self, key_hash: str) -> str:
        """
        Get the path to the metadata file for a key.
        
        Args:
            key_hash: Hash of the key
            
        Returns:
            Path to the metadata file
        """
        return os.path.join(self.metadata_dir, f"{key_hash}.json")
    
    def _get_data_path(self, key_hash: str) -> str:
        """
        Get the path to the data file for a key.
        
        Args:
            key_hash: Hash of the key
            
        Returns:
            Path to the data file
        """
        return os.path.join(self.data_dir, f"{key_hash}.pickle")
    
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
            
            # Save statistics
            self._save_stats()
    
    async def _cleanup_loop(self) -> None:
        """
        Periodically clean up expired entries.
        """
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired()
                
                # Save statistics periodically
                self._save_stats()
        
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
            raise
    
    async def _cleanup_expired(self) -> None:
        """
        Clean up expired entries.
        """
        expired_keys = []
        
        # Find all metadata files
        for metadata_file in os.listdir(self.metadata_dir):
            if not metadata_file.endswith(".json"):
                continue
            
            metadata_path = os.path.join(self.metadata_dir, metadata_file)
            key_hash = metadata_file[:-5]  # Remove .json extension
            
            try:
                # Load metadata
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Check if expired
                expires_at = metadata.get("expires_at")
                if expires_at is not None and time.time() > expires_at:
                    # Delete files
                    os.remove(metadata_path)
                    
                    data_path = self._get_data_path(key_hash)
                    if os.path.exists(data_path):
                        os.remove(data_path)
                    
                    expired_keys.append(key_hash)
                    self.expirations += 1
            
            except Exception as e:
                logger.error(f"Error cleaning up cache entry {key_hash}: {e}")
        
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
        key_hash = self._get_key_hash(key)
        metadata_path = self._get_metadata_path(key_hash)
        data_path = self._get_data_path(key_hash)
        
        # Check if files exist
        if not os.path.exists(metadata_path) or not os.path.exists(data_path):
            self.misses += 1
            return None
        
        try:
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Check if expired
            expires_at = metadata.get("expires_at")
            if expires_at is not None and time.time() > expires_at:
                # Delete files
                await self.delete(key)
                self.misses += 1
                self.expirations += 1
                return None
            
            # Load data
            with open(data_path, 'rb') as f:
                value = pickle.load(f)
            
            # Update access metadata
            metadata["last_accessed_at"] = time.time()
            metadata["access_count"] = metadata.get("access_count", 0) + 1
            
            # Save updated metadata
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
            
            self.hits += 1
            return value
        
        except Exception as e:
            logger.error(f"Error getting cache entry for key {key}: {e}")
            self.misses += 1
            return None
    
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
        key_hash = self._get_key_hash(key)
        metadata_path = self._get_metadata_path(key_hash)
        data_path = self._get_data_path(key_hash)
        
        try:
            # Check if cache is full and needs eviction
            if len(os.listdir(self.metadata_dir)) >= self.max_size and not os.path.exists(metadata_path):
                # Evict least recently used entry
                await self._evict_lru()
            
            # Create metadata
            now = time.time()
            metadata = {
                "created_at": now,
                "last_accessed_at": now,
                "access_count": 0,
                "expires_at": now + ttl if ttl is not None else None
            }
            
            # Save metadata
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
            
            # Save data
            with open(data_path, 'wb') as f:
                pickle.dump(value, f)
            
            return True
        
        except Exception as e:
            logger.error(f"Error setting cache entry for key {key}: {e}")
            return False
    
    async def _evict_lru(self) -> bool:
        """
        Evict the least recently used entry from the cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find all metadata files
            metadata_files = []
            for metadata_file in os.listdir(self.metadata_dir):
                if not metadata_file.endswith(".json"):
                    continue
                
                metadata_path = os.path.join(self.metadata_dir, metadata_file)
                key_hash = metadata_file[:-5]  # Remove .json extension
                
                try:
                    # Load metadata
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    # Add to list
                    metadata_files.append((key_hash, metadata.get("last_accessed_at", 0)))
                
                except Exception as e:
                    logger.error(f"Error loading metadata for {key_hash}: {e}")
            
            if not metadata_files:
                return False
            
            # Sort by last accessed time
            metadata_files.sort(key=lambda x: x[1])
            
            # Get least recently used
            lru_key_hash = metadata_files[0][0]
            
            # Delete files
            metadata_path = self._get_metadata_path(lru_key_hash)
            data_path = self._get_data_path(lru_key_hash)
            
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            if os.path.exists(data_path):
                os.remove(data_path)
            
            self.evictions += 1
            return True
        
        except Exception as e:
            logger.error(f"Error evicting LRU entry: {e}")
            return False
    
    async def delete(self, key: K) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        key_hash = self._get_key_hash(key)
        metadata_path = self._get_metadata_path(key_hash)
        data_path = self._get_data_path(key_hash)
        
        try:
            # Delete files if they exist
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            if os.path.exists(data_path):
                os.remove(data_path)
            
            return True
        
        except Exception as e:
            logger.error(f"Error deleting cache entry for key {key}: {e}")
            return False
    
    async def exists(self, key: K) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key exists, False otherwise
        """
        key_hash = self._get_key_hash(key)
        metadata_path = self._get_metadata_path(key_hash)
        data_path = self._get_data_path(key_hash)
        
        # Check if files exist
        if not os.path.exists(metadata_path) or not os.path.exists(data_path):
            return False
        
        try:
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Check if expired
            expires_at = metadata.get("expires_at")
            if expires_at is not None and time.time() > expires_at:
                # Delete files
                await self.delete(key)
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking if key {key} exists: {e}")
            return False
    
    async def clear(self) -> bool:
        """
        Clear the cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all metadata files
            for metadata_file in os.listdir(self.metadata_dir):
                if not metadata_file.endswith(".json"):
                    continue
                
                metadata_path = os.path.join(self.metadata_dir, metadata_file)
                os.remove(metadata_path)
            
            # Delete all data files
            for data_file in os.listdir(self.data_dir):
                if not data_file.endswith(".pickle"):
                    continue
                
                data_path = os.path.join(self.data_dir, data_file)
                os.remove(data_path)
            
            return True
        
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        # Count entries
        entry_count = 0
        for metadata_file in os.listdir(self.metadata_dir):
            if metadata_file.endswith(".json"):
                entry_count += 1
        
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "type": "disk",
            "size": entry_count,
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "uptime": time.time() - self.created_at
        }
