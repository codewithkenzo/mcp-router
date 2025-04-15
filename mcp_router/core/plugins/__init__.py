"""
Plugins Package

This package provides the plugin system for the MCP Router,
allowing for dynamic extension of the router's functionality.
"""

from mcp_router.core.plugins.plugin_interface import (
    PluginInterface,
    RouterExtensionPlugin,
    ServerAdapterPlugin,
    RoutingStrategyPlugin
)
from mcp_router.core.plugins.plugin_manager import PluginManager
from mcp_router.core.plugins.config import PluginConfig

__all__ = [
    'PluginInterface',
    'RouterExtensionPlugin',
    'ServerAdapterPlugin',
    'RoutingStrategyPlugin',
    'PluginManager',
    'PluginConfig'
]
