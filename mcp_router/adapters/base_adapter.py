"""
Base Adapter Module

This module provides the base adapter interface for MCP servers,
allowing the router to interact with different types of MCP servers.
"""

import abc
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Set

logger = logging.getLogger(__name__)

class BaseAdapter(abc.ABC):
    """
    Base adapter interface for MCP servers.
    
    This class defines the interface that all MCP server adapters must implement.
    """
    
    @abc.abstractmethod
    async def can_handle_server(self, server_config: Dict[str, Any]) -> bool:
        """
        Check if this adapter can handle a specific server configuration.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            True if this adapter can handle the server, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def connect_to_server(self, server_id: str, server_config: Dict[str, Any]) -> Any:
        """
        Connect to a server using this adapter.
        
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
    
    @abc.abstractmethod
    async def get_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of tools available on a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            List of tool definitions
        """
        pass
    
    @abc.abstractmethod
    async def check_health(self, server_id: str, server_config: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Check the health of a server.
        
        Args:
            server_id: Unique identifier for the server
            server_config: Server configuration dictionary
            
        Returns:
            Tuple of (is_healthy, response_time_in_seconds)
        """
        pass
    
    @abc.abstractmethod
    def get_server_type(self) -> str:
        """
        Get the type of server this adapter handles.
        
        Returns:
            String identifier for the server type
        """
        pass
    
    @abc.abstractmethod
    def get_adapter_name(self) -> str:
        """
        Get the name of this adapter.
        
        Returns:
            String name of the adapter
        """
        pass
    
    @abc.abstractmethod
    def get_adapter_version(self) -> str:
        """
        Get the version of this adapter.
        
        Returns:
            String version of the adapter (semver format)
        """
        pass
