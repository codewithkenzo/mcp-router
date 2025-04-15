"""
Adapters Package

This package provides adapters for different types of MCP servers,
allowing the router to interact with a wide variety of MCP servers.
"""

from mcp_router.adapters.base_adapter import BaseAdapter
from mcp_router.adapters.adapter_manager import AdapterManager

__all__ = [
    'BaseAdapter',
    'AdapterManager'
]
