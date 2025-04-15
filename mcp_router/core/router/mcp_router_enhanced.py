"""
Enhanced MCP Router Module

This module provides an enhanced router for MCP queries, integrating
the server registry, metadata store, intelligent router, health monitor,
plugin system, adapter framework, and caching system.
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

from mcp_router.core.registry.server_registry import ServerRegistry
from mcp_router.core.metadata.metadata_store import MetadataStore
from mcp_router.core.router.intelligent_router import IntelligentRouter
from mcp_router.core.health.health_monitor import HealthMonitor
from mcp_router.core.plugins.plugin_manager import PluginManager
from mcp_router.core.plugins.config import PluginConfig
from mcp_router.adapters.adapter_manager import AdapterManager
from mcp_router.core.cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class MCPRouterEnhanced:
    """
    Enhanced router for MCP queries.
    
    This class integrates the server registry, metadata store,
    intelligent router, health monitor, plugin system, adapter framework,
    and caching system to provide a complete routing solution for MCP queries.
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 registry_file: Optional[str] = None,
                 db_path: Optional[str] = None,
                 openrouter_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None,
                 health_check_interval: int = 300,
                 plugin_dirs: Optional[List[str]] = None,
                 adapter_dirs: Optional[List[str]] = None,
                 use_disk_cache: bool = True,
                 memory_cache_size: int = 1000,
                 disk_cache_size: int = 10000,
                 disk_cache_dir: Optional[str] = None):
        """
        Initialize the enhanced MCP router.
        
        Args:
            config_path: Optional path to a configuration file
            registry_file: Optional path to a registry file
            db_path: Optional path to a database file
            openrouter_api_key: Optional API key for OpenRouter
            openai_api_key: Optional API key for OpenAI
            anthropic_api_key: Optional API key for Anthropic
            health_check_interval: Interval between health checks in seconds
            plugin_dirs: Optional list of directories to search for plugins
            adapter_dirs: Optional list of directories to search for adapters
            use_disk_cache: Whether to use disk caching
            memory_cache_size: Maximum number of entries in the memory cache
            disk_cache_size: Maximum number of entries in the disk cache
            disk_cache_dir: Directory to store disk cache files
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.server_registry = ServerRegistry(registry_file)
        self.metadata_store = MetadataStore(db_path)
        self.intelligent_router = IntelligentRouter(
            self.server_registry,
            self.metadata_store,
            openrouter_api_key or self.config.get("openrouter_api_key"),
            openai_api_key or self.config.get("openai_api_key"),
            anthropic_api_key or self.config.get("anthropic_api_key")
        )
        self.health_monitor = HealthMonitor(
            self.server_registry,
            self.metadata_store,
            health_check_interval
        )
        
        # Initialize plugin system
        self.plugin_manager = PluginManager(plugin_dirs)
        self.plugin_config = PluginConfig()
        
        # Initialize adapter framework
        self.adapter_manager = AdapterManager(adapter_dirs)
        
        # Initialize caching system
        self.cache_manager = CacheManager(
            memory_cache_size=memory_cache_size,
            disk_cache_size=disk_cache_size,
            disk_cache_dir=disk_cache_dir,
            use_disk_cache=use_disk_cache
        )
        
        # Track last routing decision
        self.last_routing_decision = None
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to a configuration file
            
        Returns:
            Dictionary containing configuration
        """
        if not config_path:
            config_path = os.path.expanduser("~/.mcp_router/config.json")
        
        config = {}
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
            else:
                logger.info(f"Configuration file {config_path} not found, using defaults")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
        
        return config
    
    async def initialize(self):
        """Initialize the router and its components."""
        logger.info("Initializing Enhanced MCP Router")
        
        # Initialize plugin system
        await self.plugin_manager.initialize(self)
        
        # Initialize adapter framework
        await self.adapter_manager.initialize()
        
        # Initialize caching system
        await self.cache_manager.initialize()
        
        # Load server configurations from config
        if "servers" in self.config:
            for server_id, server_config in self.config["servers"].items():
                self.server_registry.register_server(
                    server_id,
                    server_config,
                    server_config.get("capabilities", [])
                )
                
                # Store metadata
                self.metadata_store.store_server_metadata(server_id, server_config)
                
                # Connect to server using adapter
                await self.adapter_manager.connect_to_server(server_id, server_config)
        
        # Start health monitoring
        await self.health_monitor.start_monitoring()
        
        logger.info("Enhanced MCP Router initialized")
    
    async def shutdown(self):
        """Shutdown the router and its components."""
        logger.info("Shutting down Enhanced MCP Router")
        
        # Stop health monitoring
        await self.health_monitor.stop_monitoring()
        
        # Shutdown adapter framework
        await self.adapter_manager.shutdown()
        
        # Shutdown plugin system
        await self.plugin_manager.shutdown()
        
        # Shutdown caching system
        await self.cache_manager.shutdown()
        
        logger.info("Enhanced MCP Router shut down")
    
    async def route_request(self, user_query: str) -> Dict[str, Any]:
        """
        Route a user request to appropriate MCP servers.
        
        Args:
            user_query: The user's query
            
        Returns:
            Dictionary containing routing information
        """
        # Create cache key
        cache_key = f"route_request:{user_query}"
        
        # Try to get from cache
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result is not None:
            logger.info(f"Using cached routing decision for query: {user_query}")
            return cached_result
        
        logger.info(f"Routing request: {user_query}")
        
        # Select servers based on the query
        selected_servers = await self.intelligent_router.select_servers(user_query)
        
        if not selected_servers:
            logger.warning("No suitable MCP servers found for this query")
            result = {
                "query": user_query,
                "selected_servers": [],
                "routing_confidence": 0.0,
                "error": "No suitable MCP servers found for this query"
            }
            
            # Cache the result
            await self.cache_manager.set(cache_key, result, ttl=60)
            
            return result
        
        # Store routing decision
        self.last_routing_decision = {
            "query": user_query,
            "selected_servers": selected_servers,
            "routing_confidence": self.intelligent_router.get_confidence_score(),
            "timestamp": time.time()
        }
        
        logger.info(f"Selected servers: {selected_servers}")
        
        result = {
            "query": user_query,
            "selected_servers": selected_servers,
            "routing_confidence": self.intelligent_router.get_confidence_score()
        }
        
        # Cache the result
        await self.cache_manager.set(cache_key, result, ttl=60)
        
        return result
    
    async def execute_tool(self, server_id: str, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """
        Execute a tool on a server.
        
        Args:
            server_id: Unique identifier for the server
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            
        Returns:
            Result of the tool execution
        """
        # Create cache key
        cache_key = f"execute_tool:{server_id}:{tool_name}:{json.dumps(tool_args, sort_keys=True)}"
        
        # Try to get from cache
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result is not None:
            logger.info(f"Using cached result for tool {tool_name} on server {server_id}")
            return cached_result
        
        logger.info(f"Executing tool {tool_name} on server {server_id}")
        
        # Execute the tool using adapter
        try:
            result = await self.adapter_manager.execute_tool(server_id, tool_name, tool_args)
            
            # Cache the result
            await self.cache_manager.set(cache_key, result, ttl=300)
            
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name} on server {server_id}: {e}")
            raise
    
    def register_server(self, 
                       server_id: str, 
                       server_config: Dict[str, Any], 
                       capabilities: Optional[List[str]] = None) -> bool:
        """
        Register a new MCP server.
        
        Args:
            server_id: Unique identifier for the server
            server_config: Configuration for the server
            capabilities: List of capabilities provided by the server
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Register server in registry
            self.server_registry.register_server(server_id, server_config, capabilities)
            
            # Store metadata
            self.metadata_store.store_server_metadata(server_id, {
                **server_config,
                "capabilities": capabilities or []
            })
            
            # Connect to server using adapter
            asyncio.create_task(self.adapter_manager.connect_to_server(server_id, server_config))
            
            logger.info(f"Registered server: {server_id}")
            return True
        except Exception as e:
            logger.error(f"Error registering server: {e}")
            return False
    
    async def unregister_server(self, server_id: str) -> bool:
        """
        Unregister a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Disconnect from server using adapter
            await self.adapter_manager.disconnect_from_server(server_id)
            
            # Unregister server from registry
            result = self.server_registry.unregister_server(server_id)
            
            # Delete from metadata store
            if result:
                self.metadata_store.delete_server(server_id)
            
            logger.info(f"Unregistered server: {server_id}")
            return result
        except Exception as e:
            logger.error(f"Error unregistering server: {e}")
            return False
    
    async def get_server_health(self, server_id: str) -> Dict[str, Any]:
        """
        Get the health status of a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            Dictionary containing health status
        """
        return await self.health_monitor.get_server_health_status(server_id)
    
    async def get_all_server_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status for all servers.
        
        Returns:
            Dictionary of server_id to health status
        """
        return await self.health_monitor.get_all_server_health_status()
    
    def get_server_metadata(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            Dictionary containing server metadata or None if not found
        """
        return self.metadata_store.get_server_metadata(server_id)
    
    def get_servers_by_capability(self, capability: str) -> List[str]:
        """
        Get servers with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of server IDs with the specified capability
        """
        return self.server_registry.get_servers_by_capability(capability)
    
    def get_servers_by_tag(self, tag: str) -> List[str]:
        """
        Get servers with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of server IDs with the specified tag
        """
        return self.metadata_store.get_servers_by_tag(tag)
    
    def get_all_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get all capabilities in the system.
        
        Returns:
            List of dictionaries containing capability information
        """
        return self.metadata_store.get_all_capabilities()
    
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """
        Get all tags in the system.
        
        Returns:
            List of dictionaries containing tag information
        """
        return self.metadata_store.get_all_tags()
    
    async def check_server_health(self, server_id: str) -> bool:
        """
        Check the health of a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            True if the server is healthy, False otherwise
        """
        return await self.health_monitor.check_server_health(server_id)
    
    async def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze a user query to determine required capabilities.
        
        Args:
            user_query: The user's query
            
        Returns:
            Dictionary containing analysis results
        """
        return await self.intelligent_router.analyze_query(user_query)
    
    async def get_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of tools available on a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            List of tool definitions
        """
        return await self.adapter_manager.get_tools(server_id)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        return await self.cache_manager.get_stats()
    
    async def clear_cache(self) -> bool:
        """
        Clear the cache.
        
        Returns:
            True if successful, False otherwise
        """
        return await self.cache_manager.clear()
    
    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """
        Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to get
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugin_manager.get_plugin(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, Any]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary of plugin name to plugin instance
        """
        return self.plugin_manager.get_all_plugins()
    
    def get_adapter(self, adapter_name: str) -> Optional[Any]:
        """
        Get an adapter by name.
        
        Args:
            adapter_name: Name of the adapter to get
            
        Returns:
            Adapter instance or None if not found
        """
        return self.adapter_manager.get_adapter(adapter_name)
    
    def get_all_adapters(self) -> Dict[str, Any]:
        """
        Get all loaded adapters.
        
        Returns:
            Dictionary of adapter name to adapter instance
        """
        return self.adapter_manager.get_all_adapters()
