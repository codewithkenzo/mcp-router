"""
MCP Router Package

This package provides a router for MCP queries, allowing for intelligent
routing of queries to appropriate MCP servers.
"""

from mcp_router.core.router.mcp_router import MCPRouter
from mcp_router.core.router.mcp_router_enhanced import MCPRouterEnhanced

__all__ = [
    'MCPRouter',
    'MCPRouterEnhanced'
]
