"""
Plugin Manager Module

This module provides a plugin manager for the MCP Router system,
allowing for dynamic loading and management of plugins.
"""

import os
import sys
import importlib
import importlib.util
import inspect
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple, Type, TypeVar
from pathlib import Path

from mcp_router.core.plugins.plugin_interface import PluginInterface, RouterExtensionPlugin, ServerAdapterPlugin, RoutingStrategyPlugin
from mcp_router.core.plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=PluginInterface)

class PluginManager:
    """
    Manager for MCP Router plugins.
    
    This class handles the loading, initialization, and management of plugins
    that extend the functionality of the MCP Router.
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_dirs: Optional list of directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or [
            os.path.expanduser("~/.mcp_router/plugins"),
            os.path.join(os.path.dirname(__file__), "../../plugins")
        ]
        
        # Create plugin directories if they don't exist
        for plugin_dir in self.plugin_dirs:
            os.makedirs(plugin_dir, exist_ok=True)
        
        # Dictionary of loaded plugins
        self.plugins: Dict[str, PluginInterface] = {}
        
        # Dictionary of plugin types
        self.plugin_types: Dict[str, str] = {}
        
        # Reference to the router
        self.router = None
    
    async def initialize(self, router: Any) -> None:
        """
        Initialize the plugin manager with a reference to the router.
        
        Args:
            router: Reference to the MCPRouter instance
        """
        self.router = router
        
        # Discover and load plugins
        await self.discover_plugins()
    
    async def discover_plugins(self) -> None:
        """
        Discover and load plugins from the plugin directories.
        """
        logger.info("Discovering plugins...")
        
        try:
            # Get the plugins directory
            plugins_dir = os.path.join(os.path.dirname(__file__), "..", "..", "plugins")
                    
            # Check if the directory exists
            if not os.path.exists(plugins_dir):
                logger.warning(f"Plugins directory not found: {plugins_dir}")
                return
                    
            # Load each plugin module
            for filename in os.listdir(plugins_dir):
                if not (filename.endswith(".py") and not filename.startswith("__")):
                    continue
                            
                plugin_name = filename[:-3]  # Remove .py extension
                try:
                    # Import the plugin module
                    module_path = f"mcp_router.plugins.{plugin_name}"
                    module = importlib.import_module(module_path)
                                
                    # Find plugin classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                             issubclass(attr, BasePlugin) and 
                             attr is not BasePlugin):
                                            
                            # Register the plugin
                            plugin_instance = attr()
                            self.register_plugin(plugin_instance)
                            logger.info(f"Loaded plugin: {plugin_instance.name}")
                                
                except Exception as e:
                    logger.error(f"Error loading plugin {plugin_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error discovering plugins: {e}")
    
    async def shutdown(self) -> None:
        """
        Shutdown all loaded plugins.
        """
        logger.info("Shutting down plugins...")
        
        for plugin_name, plugin in self.plugins.items():
            try:
                await plugin.shutdown()
                logger.info(f"Shut down plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin_name}: {e}")
        
        self.plugins.clear()
        self.plugin_types.clear()
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to get
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: str) -> List[PluginInterface]:
        """
        Get all plugins of a specific type.
        
        Args:
            plugin_type: Type of plugins to get ("extension", "adapter", "routing")
            
        Returns:
            List of plugin instances
        """
        return [
            plugin for plugin_name, plugin in self.plugins.items()
            if self.plugin_types.get(plugin_name) == plugin_type
        ]
    
    def get_plugin_of_type(self, plugin_type: Type[T]) -> List[T]:
        """
        Get all plugins of a specific interface type.
        
        Args:
            plugin_type: Interface type to filter by
            
        Returns:
            List of plugin instances implementing the specified interface
        """
        return [
            plugin for plugin in self.plugins.values()
            if isinstance(plugin, plugin_type)
        ]
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary of plugin name to plugin instance
        """
        return self.plugins.copy()
