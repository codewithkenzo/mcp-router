"""
Router Package

This package provides routing functionality for the MCP Router system,
allowing for intelligent routing of queries to appropriate MCP servers.
"""

from mcp_router.core.router.mcp_router import MCPRouter
from mcp_router.core.router.mcp_router_enhanced import MCPRouterEnhanced
from mcp_router.core.router.intelligent_router import IntelligentRouter

__all__ = [
    'MCPRouter',
    'MCPRouterEnhanced',
    'IntelligentRouter'
]
