"""
Cache Package

This package provides caching functionality for the MCP Router system,
allowing for efficient storage and retrieval of data.
"""

from mcp_router.core.cache.cache_interface import CacheInterface, CacheEntry
from mcp_router.core.cache.cache_manager import CacheManager

__all__ = [
    'CacheInterface',
    'CacheEntry',
    'CacheManager'
]
