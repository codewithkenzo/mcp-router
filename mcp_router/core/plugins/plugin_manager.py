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
        
        for plugin_dir in self.plugin_dirs:
            plugin_dir_path = Path(plugin_dir)
            if not plugin_dir_path.exists():
                logger.warning(f"Plugin directory {plugin_dir} does not exist")
                continue
            
            logger.info(f"Searching for plugins in {plugin_dir}")
            
            # Find all Python files in the plugin directory
            for plugin_file in plugin_dir_path.glob("**/*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                
                try:
                    # Load the plugin module
                    module_name = f"mcp_router_plugin_{plugin_file.stem}"
                    spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                    if spec is None or spec.loader is None:
                        logger.warning(f"Could not load plugin from {plugin_file}")
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find plugin classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, PluginInterface) and 
                            obj != PluginInterface and
                            obj != RouterExtensionPlugin and
                            obj != ServerAdapterPlugin and
                            obj != RoutingStrategyPlugin):
                            
                            try:
                                # Instantiate the plugin
                                plugin = obj()
                                
                                # Get plugin metadata
                                plugin_name = plugin.get_name()
                                plugin_version = plugin.get_version()
                                plugin_description = plugin.get_description()
                                
                                # Determine plugin type
                                plugin_type = "unknown"
                                if isinstance(plugin, RouterExtensionPlugin):
                                    plugin_type = "extension"
                                elif isinstance(plugin, ServerAdapterPlugin):
                                    plugin_type = "adapter"
                                elif isinstance(plugin, RoutingStrategyPlugin):
                                    plugin_type = "routing"
                                
                                # Check if plugin with same name is already loaded
                                if plugin_name in self.plugins:
                                    logger.warning(f"Plugin {plugin_name} is already loaded, skipping")
                                    continue
                                
                                # Initialize the plugin
                                if await plugin.initialize(self.router):
                                    # Add plugin to the registry
                                    self.plugins[plugin_name] = plugin
                                    self.plugin_types[plugin_name] = plugin_type
                                    
                                    logger.info(f"Loaded plugin: {plugin_name} v{plugin_version} ({plugin_type})")
                                else:
                                    logger.warning(f"Failed to initialize plugin: {plugin_name}")
                            
                            except Exception as e:
                                logger.error(f"Error loading plugin from {plugin_file}: {e}")
                
                except Exception as e:
                    logger.error(f"Error loading plugin module from {plugin_file}: {e}")
        
        logger.info(f"Discovered {len(self.plugins)} plugins")
    
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
