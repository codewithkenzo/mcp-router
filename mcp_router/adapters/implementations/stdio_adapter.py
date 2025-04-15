"""
Stdio Adapter Module

This module provides an adapter for stdio-based MCP servers,
allowing the router to interact with MCP servers that use stdio for communication.
"""

import os
import json
import logging
import time
import asyncio
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path

from mcp_router.adapters.base_adapter import BaseAdapter

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP_SDK = True
except ImportError:
    HAS_MCP_SDK = False

logger = logging.getLogger(__name__)

class StdioAdapter(BaseAdapter):
    """
    Adapter for stdio-based MCP servers.
    
    This adapter allows the router to interact with MCP servers that use
    stdio for communication, such as those created with the MCP SDK.
    """
    
    def __init__(self):
        """
        Initialize the stdio adapter.
        """
        self.connections: Dict[str, Any] = {}
        self.server_processes: Dict[str, subprocess.Popen] = {}
        self.server_configs: Dict[str, Dict[str, Any]] = {}
        self.tools_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    async def can_handle_server(self, server_config: Dict[str, Any]) -> bool:
        """
        Check if this adapter can handle a specific server configuration.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            True if this adapter can handle the server, False otherwise
        """
        # Check if the MCP SDK is installed
        if not HAS_MCP_SDK:
            logger.warning("MCP SDK not installed, cannot handle stdio servers")
            return False
        
        # Check if the server type is stdio
        server_type = server_config.get("server_type", "").lower()
        if server_type == "stdio":
            return True
        
        # Check if the server has command and args
        return "command" in server_config and "args" in server_config
    
    async def connect_to_server(self, server_id: str, server_config: Dict[str, Any]) -> Any:
        """
        Connect to a server using this adapter.
        
        Args:
            server_id: Unique identifier for the server
            server_config: Server configuration dictionary
            
        Returns:
            Connection object or client for the server
        """
        if not HAS_MCP_SDK:
            raise ImportError("MCP SDK not installed, cannot connect to stdio servers")
        
        # Store the server configuration
        self.server_configs[server_id] = server_config
        
        # Get command and args
        command = server_config.get("command", "")
        args = server_config.get("args", [])
        if isinstance(args, str):
            args = json.loads(args)
        
        # Get environment variables
        env = server_config.get("env", {})
        if isinstance(env, str):
            env = json.loads(env)
        
        # Create environment for the process
        process_env = os.environ.copy()
        process_env.update(env)
        
        # Create server parameters
        server_params = StdioServerParameters(command, args)
        
        # Start the server process
        try:
            # Create a connection to the server
            read, write = await stdio_client(server_params)
            session = ClientSession(read, write)
            await session.initialize()
            
            # Store the connection
            self.connections[server_id] = session
            
            logger.info(f"Connected to stdio server {server_id}")
            return session
        
        except Exception as e:
            logger.error(f"Error connecting to stdio server {server_id}: {e}")
            raise
    
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
            logger.warning(f"Not connected to stdio server {server_id}")
            return True
        
        try:
            # Close the session
            session = self.connections[server_id]
            await session.close()
            
            # Clean up
            del self.connections[server_id]
            if server_id in self.server_configs:
                del self.server_configs[server_id]
            if server_id in self.tools_cache:
                del self.tools_cache[server_id]
            
            logger.info(f"Disconnected from stdio server {server_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error disconnecting from stdio server {server_id}: {e}")
            
            # Clean up anyway
            if server_id in self.connections:
                del self.connections[server_id]
            if server_id in self.server_configs:
                del self.server_configs[server_id]
            if server_id in self.tools_cache:
                del self.tools_cache[server_id]
            
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
            raise ValueError(f"Not connected to stdio server {server_id}")
        
        # Get the session
        session = self.connections[server_id]
        
        # Execute the tool
        try:
            result = await session.call_tool(tool_name, tool_args)
            return result
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name} on stdio server {server_id}: {e}")
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
            raise ValueError(f"Not connected to stdio server {server_id}")
        
        # Check if tools are cached
        if server_id in self.tools_cache:
            return self.tools_cache[server_id]
        
        # Get the session
        session = self.connections[server_id]
        
        # Get the tools
        try:
            tools_response = await session.list_tools()
            
            # Convert tools to a more usable format
            tools = []
            for tool_data in tools_response.tools:
                try:
                    (internal_name, external_name), (internal_desc, external_desc), schema_list = tool_data
                    
                    if not schema_list or len(schema_list) < 2 or not isinstance(schema_list[1], dict):
                        logger.warning(f"Invalid schema for tool {external_name}: {schema_list}")
                        continue
                    
                    schema = schema_list[1]
                    
                    tool = {
                        "name": external_name,
                        "description": external_desc,
                        "schema": schema
                    }
                    
                    tools.append(tool)
                
                except Exception as e:
                    logger.error(f"Error parsing tool data: {e}")
                    continue
            
            # Cache the tools
            self.tools_cache[server_id] = tools
            
            return tools
        
        except Exception as e:
            logger.error(f"Error getting tools from stdio server {server_id}: {e}")
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
        # If already connected, check if the connection is still valid
        if server_id in self.connections:
            start_time = time.time()
            try:
                # Try to list tools as a health check
                session = self.connections[server_id]
                await session.list_tools()
                
                response_time = time.time() - start_time
                return True, response_time
            
            except Exception as e:
                logger.error(f"Health check failed for stdio server {server_id}: {e}")
                response_time = time.time() - start_time
                return False, response_time
        
        # If not connected, try to connect
        start_time = time.time()
        try:
            # Try to connect to the server
            await self.connect_to_server(server_id, server_config)
            
            # Disconnect immediately
            await self.disconnect_from_server(server_id)
            
            response_time = time.time() - start_time
            return True, response_time
        
        except Exception as e:
            logger.error(f"Health check failed for stdio server {server_id}: {e}")
            response_time = time.time() - start_time
            return False, response_time
    
    def get_server_type(self) -> str:
        """
        Get the type of server this adapter handles.
        
        Returns:
            String identifier for the server type
        """
        return "stdio"
    
    def get_adapter_name(self) -> str:
        """
        Get the name of this adapter.
        
        Returns:
            String name of the adapter
        """
        return "stdio_adapter"
    
    def get_adapter_version(self) -> str:
        """
        Get the version of this adapter.
        
        Returns:
            String version of the adapter (semver format)
        """
        return "1.0.0"
