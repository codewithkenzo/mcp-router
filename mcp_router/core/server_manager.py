"""
MCP server manager.
Handles the management of MCP servers, including configuration, installation, and lifecycle.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union, Set
import mcp
from mcp import ClientSession

from ..server_management.config import MCPServerConfig
from ..server_management.installer import MCPServerInstaller
from ..server_management.lifecycle import MCPServerLifecycle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manages MCP servers, providing a unified interface for interacting with them."""
    
    def __init__(self, config_path: Optional[str] = None,
                 registry_path: Optional[str] = None,
                 install_dir: str = "~/.mcp/servers",
                 pid_dir: str = "~/.mcp/pids"):
        """
        Initialize the server manager.
        
        Args:
            config_path: Path to the MCP server config file.
            registry_path: Path to the MCP server registry file.
            install_dir: Directory to install servers to.
            pid_dir: Directory to store PID files.
        """
        self.config = MCPServerConfig(config_path)
        self.installer = MCPServerInstaller(install_dir=install_dir, registry_path=registry_path)
        self.lifecycle = MCPServerLifecycle(pid_dir=pid_dir)
        self.client: Optional[ClientSession] = None
        self.connected_servers: Set[str] = set()
    
    async def initialize_client(self) -> None:
        """Initialize the MCP client for interacting with servers."""
        if self.client is None:
            # Create pipes for client communication
            read_pipe_r, read_pipe_w = os.pipe()
            write_pipe_r, write_pipe_w = os.pipe()
            
            # Create file objects from the pipes
            read_stream = os.fdopen(read_pipe_r, "rb")
            write_stream = os.fdopen(write_pipe_w, "wb")
            
            # Initialize the ClientSession with the streams
            self.client = ClientSession(read_stream, write_stream)
            await self.client.connect()
            
    async def list_available_servers(self) -> Dict[str, Any]:
        """
        List all available servers in the registry.
        
        Returns:
            Dictionary of available servers.
        """
        return self.installer.get_available_servers()
    
    async def list_configured_servers(self) -> Dict[str, Any]:
        """
        List all configured servers.
        
        Returns:
            Dictionary of configured servers.
        """
        return self.config.get_all_servers()
    
    async def list_running_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        List all running servers.
        
        Returns:
            Dictionary of running server statuses.
        """
        return self.lifecycle.get_all_servers_status()
    
    async def install_server(self, server_id: str, config_overrides: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Install a server.
        
        Args:
            server_id: Identifier of the server to install.
            config_overrides: Optional overrides for the server configuration.
            
        Returns:
            Tuple of (success, output, server_config).
        """
        success, output, server_config = self.installer.install_server(server_id, config_overrides)
        
        if success and server_config:
            # Add the server to the configuration
            self.config.add_server(
                server_id=server_id,
                command=server_config["command"],
                args=server_config["args"],
                env=server_config["env"]
            )
        
        return success, output, server_config
    
    async def uninstall_server(self, server_id: str) -> Tuple[bool, str]:
        """
        Uninstall a server.
        
        Args:
            server_id: Identifier of the server to uninstall.
            
        Returns:
            Tuple of (success, output).
        """
        # First, stop the server if it's running
        status = self.lifecycle.get_server_status(server_id)
        if status["running"]:
            self.lifecycle.stop_server(server_id, force=True)
        
        # Remove the server from the configuration
        try:
            self.config.remove_server(server_id)
        except KeyError:
            pass  # Server not in config, that's okay
        
        # Uninstall the server
        return self.installer.uninstall_server(server_id)
    
    async def start_server(self, server_id: str) -> Tuple[bool, Optional[str]]:
        """
        Start a server.
        
        Args:
            server_id: Identifier of the server to start.
            
        Returns:
            Tuple of (success, error_message).
        """
        server_config = self.config.get_server_config(server_id)
        if not server_config:
            return False, f"Server '{server_id}' not found in configuration"
        
        success, error = self.lifecycle.start_server(
            server_id=server_id,
            command=server_config["command"],
            args=server_config.get("args", []),
            env=server_config.get("env", {})
        )
        
        # If the server started successfully, connect to it
        if success and self.client:
            try:
                await self.client.connect_to_servers()
                self.connected_servers.add(server_id)
            except Exception as e:
                logger.warning(f"Failed to connect to server '{server_id}': {e}")
                # But we still consider the server started
        
        return success, error
    
    async def stop_server(self, server_id: str, force: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Stop a server.
        
        Args:
            server_id: Identifier of the server to stop.
            force: Whether to forcefully terminate the process.
            
        Returns:
            Tuple of (success, error_message).
        """
        success, error = self.lifecycle.stop_server(server_id, force=force)
        
        # Update connected servers
        if success and server_id in self.connected_servers:
            self.connected_servers.remove(server_id)
        
        return success, error
    
    async def restart_server(self, server_id: str) -> Tuple[bool, Optional[str]]:
        """
        Restart a server.
        
        Args:
            server_id: Identifier of the server to restart.
            
        Returns:
            Tuple of (success, error_message).
        """
        # Stop the server
        stop_success, stop_error = await self.stop_server(server_id)
        
        # Wait a bit for the server to fully stop
        await asyncio.sleep(1)
        
        # Start the server
        start_success, start_error = await self.start_server(server_id)
        
        # If either operation failed, return the error
        if not stop_success:
            return False, f"Failed to stop server: {stop_error}"
        
        if not start_success:
            return False, f"Failed to start server: {start_error}"
        
        return True, None
    
    async def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """
        Get the status of a server.
        
        Args:
            server_id: Identifier of the server.
            
        Returns:
            Dictionary with status information.
        """
        return self.lifecycle.get_server_status(server_id)
    
    async def get_server_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """
        Get the tools provided by a server.
        
        Args:
            server_id: Identifier of the server.
            
        Returns:
            List of tool definitions.
        """
        if not self.client:
            await self.initialize_client()
            
        try:
            return await self.client.get_tools(server_id)
        except Exception as e:
            logger.error(f"Error getting tools for server '{server_id}': {e}")
            return []
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on a server.
        
        Args:
            server_id: Identifier of the server.
            tool_name: Name of the tool to call.
            arguments: Arguments for the tool.
            
        Returns:
            Result of the tool call.
            
        Raises:
            ValueError: If the server is not connected.
            RuntimeError: If the tool call fails.
        """
        if not self.client:
            await self.initialize_client()
            
        # Make sure the server is in the connected servers list
        if server_id not in self.connected_servers:
            # Try to connect to the server
            server_status = self.lifecycle.get_server_status(server_id)
            if not server_status["running"]:
                await self.start_server(server_id)
            
            await self.client.connect_to_servers()
            self.connected_servers.add(server_id)
        
        try:
            return await self.client.call_tool(server_id, tool_name, arguments)
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on server '{server_id}': {e}")
            raise RuntimeError(f"Failed to call tool '{tool_name}' on server '{server_id}': {str(e)}")
    
    async def create_custom_server(self, server_id: str, command: str, args: List[str] = None, 
                                  env: Dict[str, str] = None, save_to_registry: bool = True) -> Tuple[bool, str]:
        """
        Create a custom server configuration.
        
        Args:
            server_id: Unique identifier for the server.
            command: Command to start the server.
            args: Command arguments.
            env: Environment variables.
            save_to_registry: Whether to save to the custom registry.
            
        Returns:
            Tuple of (success, message).
        """
        # Add the server to the configuration
        self.config.add_server(
            server_id=server_id,
            command=command,
            args=args or [],
            env=env or {}
        )
        
        # Optionally save to the custom registry
        if save_to_registry:
            server_info = {
                "name": server_id,
                "description": f"Custom server: {command}",
                "command": command,
                "args": args or [],
                "env": env or {},
                "install_type": "custom"
            }
            
            success, message = self.installer.create_custom_registry_entry(server_id, server_info)
            if not success:
                logger.warning(f"Failed to save custom server to registry: {message}")
                # But we still consider the server created since it's in the config
        
        return True, f"Created custom server '{server_id}'"
    
    async def get_server_info(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a server.
        
        Args:
            server_id: Identifier of the server.
            
        Returns:
            Server information dictionary, or None if not found.
        """
        # Check the registry first
        server_info = self.installer.get_server_info(server_id)
        
        # If not in registry, check the configuration
        if not server_info:
            server_config = self.config.get_server_config(server_id)
            if server_config:
                server_info = {
                    "name": server_id,
                    "description": f"Custom server: {server_config.get('command', '')}",
                    "command": server_config.get("command", ""),
                    "args": server_config.get("args", []),
                    "env": server_config.get("env", {}),
                    "install_type": "custom"
                }
        
        return server_info
    
    async def get_client(self) -> ClientSession:
        """
        Get the MCP client.
        
        Returns:
            The initialized MCP client.
        """
        if not self.client:
            await self.initialize_client()
        
        return self.client
    
    async def close(self) -> None:
        """Close the server manager and clean up resources."""
        if self.client:
            await self.client.close()
            self.client = None


# Example usage (async context required)
"""
async def example():
    # Initialize the server manager
    manager = MCPServerManager()
    
    # List available servers
    available_servers = await manager.list_available_servers()
    print(f"Available servers: {list(available_servers.keys())}")
    
    # Install and start a server
    server_id = "example_server"
    success, output, config = await manager.install_server(server_id)
    if success:
        print(f"Installed server '{server_id}'")
        
        # Start the server
        start_success, error = await manager.start_server(server_id)
        if start_success:
            print(f"Started server '{server_id}'")
            
            # Get server status
            status = await manager.get_server_status(server_id)
            print(f"Server status: {status}")
            
            # Get server tools
            tools = await manager.get_server_tools(server_id)
            print(f"Server provides {len(tools)} tools")
            
            # Call a tool
            if tools:
                tool_name = tools[0]["name"]
                result = await manager.call_tool(server_id, tool_name, {})
                print(f"Tool result: {result}")
            
            # Stop the server
            await manager.stop_server(server_id)
            print(f"Stopped server '{server_id}'")
    
    # Close the manager
    await manager.close()
"""
