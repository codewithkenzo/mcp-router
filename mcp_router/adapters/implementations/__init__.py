"""
Adapter Implementations Package

This package provides implementations of adapters for different types of MCP servers.
"""

# Import adapters so they can be discovered
try:
    from mcp_router.adapters.implementations.stdio_adapter import StdioAdapter
except ImportError:
    pass

__all__ = [
    'StdioAdapter'
]
