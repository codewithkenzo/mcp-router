"""
Configuration management for MCP servers.
Handles reading, parsing, and updating MCP server configurations.
"""

import os
import json
import yaml
import toml
from typing import Dict, Any, List, Optional
from pathlib import Path

DEFAULT_CONFIG_PATHS = [
    "~/.mcp/config.json",
    "~/.config/mcp/config.json",
    "./mcp_config.json"
]

class MCPServerConfig:
    """Manages configurations for MCP servers."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the config file. If None, searches DEFAULT_CONFIG_PATHS.
        """
        self.config_path = self._find_config_file(config_path)
        self.config = self._load_config()
    
    def _find_config_file(self, config_path: Optional[str] = None) -> str:
        """
        Find the configuration file.
        
        Args:
            config_path: Path to the config file. If None, searches DEFAULT_CONFIG_PATHS.
            
        Returns:
            Path to the config file.
            
        Raises:
            FileNotFoundError: If no config file is found.
        """
        if config_path and os.path.exists(os.path.expanduser(config_path)):
            return os.path.expanduser(config_path)
        
        for path in DEFAULT_CONFIG_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                return expanded_path
        
        # If no config file found, create a new one in the first default location
        default_path = os.path.expanduser(DEFAULT_CONFIG_PATHS[0])
        os.makedirs(os.path.dirname(default_path), exist_ok=True)
        
        with open(default_path, 'w') as f:
            json.dump({"mcpServers": {}}, f, indent=2)
        
        return default_path
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration file.
        
        Returns:
            Parsed configuration dictionary.
        """
        with open(self.config_path, 'r') as f:
            if self.config_path.endswith('.json'):
                return json.load(f)
            elif self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                return yaml.safe_load(f)
            elif self.config_path.endswith('.toml'):
                return toml.load(f)
            else:
                # Default to JSON
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"mcpServers": {}}
    
    def save_config(self) -> None:
        """Save the current configuration to the config file."""
        with open(self.config_path, 'w') as f:
            if self.config_path.endswith('.json'):
                json.dump(self.config, f, indent=2)
            elif self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                yaml.safe_dump(self.config, f)
            elif self.config_path.endswith('.toml'):
                toml.dump(self.config, f)
            else:
                # Default to JSON
                json.dump(self.config, f, indent=2)
    
    def get_server_config(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific server.
        
        Args:
            server_id: The ID of the server.
            
        Returns:
            Server configuration dictionary, or None if not found.
        """
        return self.config.get("mcpServers", {}).get(server_id)
    
    def get_all_servers(self) -> Dict[str, Any]:
        """
        Get all server configurations.
        
        Returns:
            Dictionary of server configurations.
        """
        return self.config.get("mcpServers", {})
    
    def add_server(self, server_id: str, command: str, args: List[str] = None, env: Dict[str, str] = None) -> None:
        """
        Add a new server configuration.
        
        Args:
            server_id: Unique identifier for the server.
            command: Command to start the server.
            args: List of command arguments.
            env: Dictionary of environment variables.
        """
        if "mcpServers" not in self.config:
            self.config["mcpServers"] = {}
        
        self.config["mcpServers"][server_id] = {
            "command": command,
            "args": args or [],
            "env": env or {}
        }
        
        self.save_config()
    
    def update_server(self, server_id: str, command: Optional[str] = None, 
                      args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> None:
        """
        Update an existing server configuration.
        
        Args:
            server_id: Unique identifier for the server.
            command: New command to start the server.
            args: New list of command arguments.
            env: New dictionary of environment variables.
            
        Raises:
            KeyError: If the server does not exist.
        """
        if "mcpServers" not in self.config or server_id not in self.config["mcpServers"]:
            raise KeyError(f"Server '{server_id}' does not exist in configuration")
        
        server_config = self.config["mcpServers"][server_id]
        
        if command:
            server_config["command"] = command
        
        if args is not None:
            server_config["args"] = args
        
        if env is not None:
            server_config["env"] = env
        
        self.save_config()
    
    def remove_server(self, server_id: str) -> None:
        """
        Remove a server configuration.
        
        Args:
            server_id: Unique identifier for the server.
            
        Raises:
            KeyError: If the server does not exist.
        """
        if "mcpServers" not in self.config or server_id not in self.config["mcpServers"]:
            raise KeyError(f"Server '{server_id}' does not exist in configuration")
        
        del self.config["mcpServers"][server_id]
        self.save_config()
    
    def merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge a new configuration with the existing one.
        
        Args:
            new_config: New configuration to merge.
        """
        if "mcpServers" in new_config:
            if "mcpServers" not in self.config:
                self.config["mcpServers"] = {}
            
            for server_id, server_config in new_config["mcpServers"].items():
                self.config["mcpServers"][server_id] = server_config
        
        self.save_config()


# Example usage
if __name__ == "__main__":
    config = MCPServerConfig()
    print(f"Config file located at: {config.config_path}")
    
    # List all configured servers
    servers = config.get_all_servers()
    print(f"Found {len(servers)} configured servers:")
    for server_id, server_config in servers.items():
        print(f"  - {server_id}: {server_config['command']} {' '.join(server_config.get('args', []))}")
        
    # Add a new test server
    try:
        config.add_server(
            server_id="test_server",
            command="python",
            args=["-m", "mcp.server"],
            env={"MCP_PORT": "5678"}
        )
        print("Added test_server configuration")
    except Exception as e:
        print(f"Error adding server: {e}")
