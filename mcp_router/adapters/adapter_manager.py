"""
Adapter Manager Module

This module provides a manager for MCP server adapters,
allowing the router to interact with different types of MCP servers.
"""

import os
import logging
import importlib
import importlib.util
import inspect
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set, Type
from pathlib import Path

from mcp_router.adapters.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)

class AdapterManager:
    """
    Manager for MCP server adapters.
    
    This class handles the loading, initialization, and management of adapters
    that allow the router to interact with different types of MCP servers.
    """
    
    def __init__(self, adapter_dirs: Optional[List[str]] = None):
        """
        Initialize the adapter manager.
        
        Args:
            adapter_dirs: Optional list of directories to search for adapters
        """
        self.adapter_dirs = adapter_dirs or [
            os.path.join(os.path.dirname(__file__), "implementations")
        ]
        
        # Create adapter directories if they don't exist
        for adapter_dir in self.adapter_dirs:
            os.makedirs(adapter_dir, exist_ok=True)
        
        # Dictionary of loaded adapters by name
        self.adapters: Dict[str, BaseAdapter] = {}
        
        # Dictionary of adapters by server type
        self.adapters_by_type: Dict[str, List[BaseAdapter]] = {}
        
        # Dictionary of active connections by server ID
        self.connections: Dict[str, Any] = {}
        
        # Dictionary mapping server IDs to adapter names
        self.server_adapters: Dict[str, str] = {}
    
    async def initialize(self) -> None:
        """
        Initialize the adapter manager.
        """
        logger.info("Initializing adapter manager...")
        
        # Discover and load adapters
        await self.discover_adapters()
    
    async def discover_adapters(self) -> None:
        """
        Discover and load adapters from the adapter directories.
        """
        logger.info("Discovering adapters...")
        
        for adapter_dir in self.adapter_dirs:
            adapter_dir_path = Path(adapter_dir)
            if not adapter_dir_path.exists():
                logger.warning(f"Adapter directory {adapter_dir} does not exist")
                continue
            
            logger.info(f"Searching for adapters in {adapter_dir}")
            
            # Find all Python files in the adapter directory
            for adapter_file in adapter_dir_path.glob("**/*.py"):
                if adapter_file.name.startswith("_"):
                    continue
                
                try:
                    # Load the adapter module
                    module_name = f"mcp_router_adapter_{adapter_file.stem}"
                    spec = importlib.util.spec_from_file_location(module_name, adapter_file)
                    if spec is None or spec.loader is None:
                        logger.warning(f"Could not load adapter from {adapter_file}")
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find adapter classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseAdapter) and 
                            obj != BaseAdapter):
                            
                            try:
                                # Instantiate the adapter
                                adapter = obj()
                                
                                # Get adapter metadata
                                adapter_name = adapter.get_adapter_name()
                                adapter_version = adapter.get_adapter_version()
                                server_type = adapter.get_server_type()
                                
                                # Check if adapter with same name is already loaded
                                if adapter_name in self.adapters:
                                    logger.warning(f"Adapter {adapter_name} is already loaded, skipping")
                                    continue
                                
                                # Add adapter to the registry
                                self.adapters[adapter_name] = adapter
                                
                                # Add adapter to the server type registry
                                if server_type not in self.adapters_by_type:
                                    self.adapters_by_type[server_type] = []
                                self.adapters_by_type[server_type].append(adapter)
                                
                                logger.info(f"Loaded adapter: {adapter_name} v{adapter_version} for server type: {server_type}")
                            
                            except Exception as e:
                                logger.error(f"Error loading adapter from {adapter_file}: {e}")
                
                except Exception as e:
                    logger.error(f"Error loading adapter module from {adapter_file}: {e}")
        
        logger.info(f"Discovered {len(self.adapters)} adapters for {len(self.adapters_by_type)} server types")
    
    async def shutdown(self) -> None:
        """
        Shutdown the adapter manager and disconnect from all servers.
        """
        logger.info("Shutting down adapter manager...")
        
        # Disconnect from all servers
        for server_id in list(self.connections.keys()):
            try:
                await self.disconnect_from_server(server_id)
            except Exception as e:
                logger.error(f"Error disconnecting from server {server_id}: {e}")
        
        self.adapters.clear()
        self.adapters_by_type.clear()
        self.connections.clear()
        self.server_adapters.clear()
    
    async def get_adapter_for_server(self, server_config: Dict[str, Any]) -> Optional[BaseAdapter]:
        """
        Get an adapter that can handle a specific server configuration.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            Adapter instance or None if no adapter can handle the server
        """
        # Check if server_type is specified in the configuration
        server_type = server_config.get("server_type")
        if server_type and server_type in self.adapters_by_type:
            # Try adapters for the specified server type
            for adapter in self.adapters_by_type[server_type]:
                try:
                    if await adapter.can_handle_server(server_config):
                        return adapter
                except Exception as e:
                    logger.error(f"Error checking if adapter {adapter.get_adapter_name()} can handle server: {e}")
        
        # If no adapter found for the specified server type, try all adapters
        for adapter in self.adapters.values():
            try:
                if await adapter.can_handle_server(server_config):
                    return adapter
            except Exception as e:
                logger.error(f"Error checking if adapter {adapter.get_adapter_name()} can handle server: {e}")
        
        return None
    
    async def connect_to_server(self, server_id: str, server_config: Dict[str, Any]) -> bool:
        """
        Connect to a server using an appropriate adapter.
        
        Args:
            server_id: Unique identifier for the server
            server_config: Server configuration dictionary
            
        Returns:
            True if connection was successful, False otherwise
        """
        # Check if already connected
        if server_id in self.connections:
            logger.info(f"Already connected to server {server_id}")
            return True
        
        # Get an adapter for the server
        adapter = await self.get_adapter_for_server(server_config)
        if not adapter:
            logger.error(f"No adapter found for server {server_id}")
            return False
        
        try:
            # Connect to the server
            connection = await adapter.connect_to_server(server_id, server_config)
            
            # Store the connection and adapter
            self.connections[server_id] = connection
            self.server_adapters[server_id] = adapter.get_adapter_name()
            
            logger.info(f"Connected to server {server_id} using adapter {adapter.get_adapter_name()}")
            return True
        
        except Exception as e:
            logger.error(f"Error connecting to server {server_id}: {e}")
            return False
    
    async def disconnect_from_server(self, server_id: str) -> bool:
        """
        Disconnect from a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            True if disconnection was successful, False otherwise
        """
        # Check if connected
        if server_id not in self.connections:
            logger.warning(f"Not connected to server {server_id}")
            return True
        
        # Get the adapter
        adapter_name = self.server_adapters.get(server_id)
        if not adapter_name or adapter_name not in self.adapters:
            logger.error(f"No adapter found for server {server_id}")
            
            # Clean up connection anyway
            if server_id in self.connections:
                del self.connections[server_id]
            if server_id in self.server_adapters:
                del self.server_adapters[server_id]
            
            return False
        
        adapter = self.adapters[adapter_name]
        
        try:
            # Disconnect from the server
            result = await adapter.disconnect_from_server(server_id)
            
            # Clean up connection
            if server_id in self.connections:
                del self.connections[server_id]
            if server_id in self.server_adapters:
                del self.server_adapters[server_id]
            
            logger.info(f"Disconnected from server {server_id}")
            return result
        
        except Exception as e:
            logger.error(f"Error disconnecting from server {server_id}: {e}")
            
            # Clean up connection anyway
            if server_id in self.connections:
                del self.connections[server_id]
            if server_id in self.server_adapters:
                del self.server_adapters[server_id]
            
            return False
    
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
        # Check if connected
        if server_id not in self.connections:
            raise ValueError(f"Not connected to server {server_id}")
        
        # Get the adapter
        adapter_name = self.server_adapters.get(server_id)
        if not adapter_name or adapter_name not in self.adapters:
            raise ValueError(f"No adapter found for server {server_id}")
        
        adapter = self.adapters[adapter_name]
        
        # Execute the tool
        start_time = time.time()
        try:
            result = await adapter.execute_tool(server_id, tool_name, tool_args)
            execution_time = time.time() - start_time
            
            logger.info(f"Executed tool {tool_name} on server {server_id} in {execution_time:.3f}s")
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing tool {tool_name} on server {server_id} after {execution_time:.3f}s: {e}")
            raise
    
    async def get_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of tools available on a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            List of tool definitions
        """
        # Check if connected
        if server_id not in self.connections:
            raise ValueError(f"Not connected to server {server_id}")
        
        # Get the adapter
        adapter_name = self.server_adapters.get(server_id)
        if not adapter_name or adapter_name not in self.adapters:
            raise ValueError(f"No adapter found for server {server_id}")
        
        adapter = self.adapters[adapter_name]
        
        # Get the tools
        try:
            tools = await adapter.get_tools(server_id)
            logger.info(f"Got {len(tools)} tools from server {server_id}")
            return tools
        
        except Exception as e:
            logger.error(f"Error getting tools from server {server_id}: {e}")
            raise
    
    async def check_health(self, server_id: str, server_config: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Check the health of a server.
        
        Args:
            server_id: Unique identifier for the server
            server_config: Server configuration dictionary
            
        Returns:
            Tuple of (is_healthy, response_time_in_seconds)
        """
        # Get an adapter for the server
        adapter = None
        
        # If already connected, use the existing adapter
        if server_id in self.server_adapters:
            adapter_name = self.server_adapters[server_id]
            if adapter_name in self.adapters:
                adapter = self.adapters[adapter_name]
        
        # Otherwise, find an adapter that can handle the server
        if not adapter:
            adapter = await self.get_adapter_for_server(server_config)
        
        if not adapter:
            logger.error(f"No adapter found for server {server_id}")
            return False, 0.0
        
        try:
            # Check the health of the server
            is_healthy, response_time = await adapter.check_health(server_id, server_config)
            
            logger.info(f"Health check for server {server_id}: {'healthy' if is_healthy else 'unhealthy'}, response time: {response_time:.3f}s")
            return is_healthy, response_time
        
        except Exception as e:
            logger.error(f"Error checking health of server {server_id}: {e}")
            return False, 0.0
    
    def get_adapter(self, adapter_name: str) -> Optional[BaseAdapter]:
        """
        Get an adapter by name.
        
        Args:
            adapter_name: Name of the adapter to get
            
        Returns:
            Adapter instance or None if not found
        """
        return self.adapters.get(adapter_name)
    
    def get_adapters_by_type(self, server_type: str) -> List[BaseAdapter]:
        """
        Get all adapters for a specific server type.
        
        Args:
            server_type: Type of server to get adapters for
            
        Returns:
            List of adapter instances
        """
        return self.adapters_by_type.get(server_type, [])
    
    def get_all_adapters(self) -> Dict[str, BaseAdapter]:
        """
        Get all loaded adapters.
        
        Returns:
            Dictionary of adapter name to adapter instance
        """
        return self.adapters.copy()
    
    def get_all_server_types(self) -> List[str]:
        """
        Get all supported server types.
        
        Returns:
            List of server type strings
        """
        return list(self.adapters_by_type.keys())
    
    def get_connected_servers(self) -> List[str]:
        """
        Get all servers that are currently connected.
        
        Returns:
            List of server IDs
        """
        return list(self.connections.keys())
