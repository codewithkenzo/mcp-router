"""
Plugin Interface Module

This module defines the interface for plugins in the MCP Router system.
"""

import abc
from typing import Dict, List, Any, Optional, Set, Tuple

class PluginInterface(abc.ABC):
    """
    Base interface for all MCP Router plugins.
    
    Plugins must implement this interface to be loaded by the plugin manager.
    """
    
    @abc.abstractmethod
    async def initialize(self, router: Any) -> bool:
        """
        Initialize the plugin.
        
        Args:
            router: Reference to the MCPRouter instance
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def shutdown(self) -> None:
        """
        Shutdown the plugin.
        """
        pass
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the plugin.
        
        Returns:
            String name of the plugin
        """
        pass
    
    @abc.abstractmethod
    def get_version(self) -> str:
        """
        Get the version of the plugin.
        
        Returns:
            String version of the plugin (semver format)
        """
        pass
    
    @abc.abstractmethod
    def get_description(self) -> str:
        """
        Get the description of the plugin.
        
        Returns:
            String description of the plugin
        """
        pass

class RouterExtensionPlugin(PluginInterface):
    """
    Interface for plugins that extend the router's functionality.
    
    These plugins can add new methods to the router or modify the behavior
    of existing methods.
    """
    
    @abc.abstractmethod
    async def handle_request(self, user_query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle a user request.
        
        Args:
            user_query: The user's query
            context: Dictionary containing context information
            
        Returns:
            Optional dictionary containing handling result or None to continue normal processing
        """
        pass

class ServerAdapterPlugin(PluginInterface):
    """
    Interface for plugins that add support for new types of MCP servers.
    
    These plugins can add support for new server types or modify the behavior
    of existing server types.
    """
    
    @abc.abstractmethod
    async def can_handle_server(self, server_config: Dict[str, Any]) -> bool:
        """
        Check if this plugin can handle a specific server configuration.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            True if this plugin can handle the server, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def connect_to_server(self, server_id: str, server_config: Dict[str, Any]) -> Any:
        """
        Connect to a server.
        
        Args:
            server_id: Unique identifier for the server
            server_config: Server configuration dictionary
            
        Returns:
            Connection object or client for the server
        """
        pass
    
    @abc.abstractmethod
    async def disconnect_from_server(self, server_id: str) -> bool:
        """
        Disconnect from a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            True if disconnection was successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
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
        pass

class RoutingStrategyPlugin(PluginInterface):
    """
    Interface for plugins that implement routing strategies.
    
    These plugins can implement different strategies for routing queries
    to appropriate MCP servers.
    """
    
    @abc.abstractmethod
    async def select_servers(self, user_query: str, available_servers: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Select servers for a user query.
        
        Args:
            user_query: The user's query
            available_servers: Dictionary of server_id to server configuration
            
        Returns:
            List of server IDs to route the query to
        """
        pass
    
    @abc.abstractmethod
    def get_confidence_score(self) -> float:
        """
        Get the confidence score for the last routing decision.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass
