"""
MCP server installer.
Handles downloading, installing, and configuring MCP servers.
"""

import os
import json
import shutil
import subprocess
import tempfile
import logging
import urllib.request
from typing import Dict, Any, Optional, List, Tuple, Union
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default locations where MCP server registry files might be found
REGISTRY_URLS = [
    "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/registry.json",
    "https://raw.githubusercontent.com/glama-ai/mcp-servers/main/registry.json",
    "https://raw.githubusercontent.com/BigSweetPotatoStudio/HyperChatMCP/main/registry.json"
]

class MCPServerInstaller:
    """Handles installation of MCP servers."""
    
    def __init__(self, install_dir: str = "~/.mcp/servers", 
                 registry_path: Optional[str] = None,
                 registry_urls: Optional[List[str]] = None,
                 config_path: Optional[str] = "~/.mcp/config.json"):
        """
        Initialize the installer.
        
        Args:
            install_dir: Directory to install servers to.
            registry_path: Path to a local registry file.
            registry_urls: URLs to download registry files from.
            config_path: Path to the MCP config file.
        """
        self.install_dir = os.path.expanduser(install_dir)
        os.makedirs(self.install_dir, exist_ok=True)
        
        self.registry_path = registry_path
        self.registry_urls = registry_urls or REGISTRY_URLS
        self.config_path = os.path.expanduser(config_path) if config_path else None
        self.registry: Dict[str, Any] = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """
        Load the MCP server registry.
        
        Returns:
            Registry dictionary.
        """
        registry = {"servers": {}}
        
        # Load from local config file first if it exists
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Extract server definitions from mcpServers section
                    if "mcpServers" in config:
                        for server_id, server_config in config["mcpServers"].items():
                            # Convert to registry format
                            registry["servers"][server_id] = {
                                "id": server_id,
                                "name": server_id,
                                "description": f"MCP server: {server_id}",
                                "command": server_config.get("command", ""),
                                "args": server_config.get("args", []),
                                "env": server_config.get("env", {}),
                                "source": "local_config"
                            }
                logger.info(f"Loaded server configurations from {self.config_path}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading config from {self.config_path}: {e}")
        
        # Load local registry if specified
        if self.registry_path and os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    local_registry = json.load(f)
                    registry["servers"].update(local_registry.get("servers", {}))
                logger.info(f"Loaded server registry from {self.registry_path}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading registry from {self.registry_path}: {e}")
        
        # Load remote registries
        for url in self.registry_urls:
            try:
                with urllib.request.urlopen(url) as response:
                    remote_registry = json.loads(response.read().decode('utf-8'))
                    registry["servers"].update(remote_registry.get("servers", {}))
                logger.info(f"Loaded server registry from {url}")
            except Exception as e:
                logger.warning(f"Error loading registry from {url}: {e}")
        
        return registry
    
    def refresh_registry(self) -> None:
        """Refresh the registry from remote sources."""
        self.registry = self._load_registry()
    
    def get_available_servers(self) -> Dict[str, Any]:
        """
        Get the list of available servers in the registry.
        
        Returns:
            Dictionary of available servers.
        """
        return self.registry.get("servers", {})
    
    def get_server_info(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific server.
        
        Args:
            server_id: Server identifier.
            
        Returns:
            Server information dictionary, or None if not found.
        """
        return self.registry.get("servers", {}).get(server_id)
    
    def _execute_command(self, command: List[str], env: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
        """
        Execute a shell command.
        
        Args:
            command: Command and arguments.
            env: Environment variables.
            
        Returns:
            Tuple of (success, output).
        """
        try:
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            process = subprocess.run(
                command,
                env=process_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True
            )
            return True, process.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stdout
        except Exception as e:
            return False, str(e)
    
    def install_npm_package(self, package_name: str) -> Tuple[bool, str]:
        """
        Install an NPM package.
        
        Args:
            package_name: Name of the package to install.
            
        Returns:
            Tuple of (success, output).
        """
        return self._execute_command(["npm", "install", "-g", package_name])
    
    def install_python_package(self, package_name: str, use_uv: bool = True) -> Tuple[bool, str]:
        """
        Install a Python package.
        
        Args:
            package_name: Name of the package to install.
            use_uv: Whether to use uv instead of pip.
            
        Returns:
            Tuple of (success, output).
        """
        if use_uv:
            return self._execute_command(["uv", "pip", "install", package_name])
        else:
            return self._execute_command(["pip", "install", package_name])
    
    def install_server(self, server_id: str, config_overrides: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Install an MCP server.
        
        Args:
            server_id: Identifier of the server to install.
            config_overrides: Optional overrides for the server configuration.
            
        Returns:
            Tuple of (success, output, server_config).
        """
        # Get server information from registry
        server_info = self.get_server_info(server_id)
        if not server_info:
            return False, f"Server '{server_id}' not found in registry", None
        
        logger.info(f"Installing MCP server '{server_id}'...")
        
        # Handle different installation types
        install_type = server_info.get("install_type", "npm")
        success = False
        output = ""
        
        if install_type == "npm":
            package_name = server_info.get("package_name")
            if not package_name:
                return False, f"No package name specified for server '{server_id}'", None
            
            success, output = self.install_npm_package(package_name)
        
        elif install_type == "python":
            package_name = server_info.get("package_name")
            if not package_name:
                return False, f"No package name specified for server '{server_id}'", None
            
            success, output = self.install_python_package(package_name)
        
        elif install_type == "docker":
            image_name = server_info.get("image_name")
            if not image_name:
                return False, f"No image name specified for server '{server_id}'", None
            
            success, output = self._execute_command(["docker", "pull", image_name])
        
        else:
            return False, f"Unsupported installation type '{install_type}' for server '{server_id}'", None
        
        if not success:
            logger.error(f"Failed to install server '{server_id}': {output}")
            return False, f"Installation failed: {output}", None
        
        # Generate server configuration
        server_config = self._generate_server_config(server_info, config_overrides)
        
        # If there's a post-install script, run it
        if "post_install_script" in server_info:
            script = server_info["post_install_script"]
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script)
            
            os.chmod(f.name, 0o755)
            post_success, post_output = self._execute_command([f.name])
            os.unlink(f.name)
            
            if not post_success:
                logger.warning(f"Post-install script failed for server '{server_id}': {post_output}")
                output += f"\nPost-install script output:\n{post_output}"
        
        logger.info(f"Successfully installed MCP server '{server_id}'")
        return True, output, server_config
    
    def _generate_server_config(self, server_info: Dict[str, Any], 
                               config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate server configuration.
        
        Args:
            server_info: Server information from the registry.
            config_overrides: Optional overrides for the configuration.
            
        Returns:
            Server configuration dictionary.
        """
        # Start with the base configuration from server_info
        config = {
            "command": server_info.get("command", ""),
            "args": server_info.get("args", []),
            "env": server_info.get("env", {})
        }
        
        # Apply any config overrides
        if config_overrides:
            if "command" in config_overrides:
                config["command"] = config_overrides["command"]
            
            if "args" in config_overrides:
                config["args"] = config_overrides["args"]
            
            if "env" in config_overrides:
                config["env"].update(config_overrides["env"])
        
        return config
    
    def uninstall_server(self, server_id: str) -> Tuple[bool, str]:
        """
        Uninstall an MCP server.
        
        Args:
            server_id: Identifier of the server to uninstall.
            
        Returns:
            Tuple of (success, output).
        """
        # Get server information from registry
        server_info = self.get_server_info(server_id)
        if not server_info:
            return False, f"Server '{server_id}' not found in registry"
        
        logger.info(f"Uninstalling MCP server '{server_id}'...")
        
        # Handle different installation types
        install_type = server_info.get("install_type", "npm")
        success = False
        output = ""
        
        if install_type == "npm":
            package_name = server_info.get("package_name")
            if not package_name:
                return False, f"No package name specified for server '{server_id}'"
            
            success, output = self._execute_command(["npm", "uninstall", "-g", package_name])
        
        elif install_type == "python":
            package_name = server_info.get("package_name")
            if not package_name:
                return False, f"No package name specified for server '{server_id}'"
            
            if server_info.get("use_uv", True):
                success, output = self._execute_command(["uv", "pip", "uninstall", "-y", package_name])
            else:
                success, output = self._execute_command(["pip", "uninstall", "-y", package_name])
        
        else:
            # For other types like Docker, there's usually no need to uninstall
            success = True
            output = f"No uninstallation needed for {install_type} server"
        
        # If there's a post-uninstall script, run it
        if "post_uninstall_script" in server_info:
            script = server_info["post_uninstall_script"]
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script)
            
            os.chmod(f.name, 0o755)
            post_success, post_output = self._execute_command([f.name])
            os.unlink(f.name)
            
            if not post_success:
                logger.warning(f"Post-uninstall script failed for server '{server_id}': {post_output}")
                output += f"\nPost-uninstall script output:\n{post_output}"
        
        if success:
            logger.info(f"Successfully uninstalled MCP server '{server_id}'")
        else:
            logger.error(f"Failed to uninstall server '{server_id}': {output}")
        
        return success, output
    
    def create_custom_registry_entry(self, server_id: str, server_info: Dict[str, Any], 
                                     save_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a custom registry entry for a server.
        
        Args:
            server_id: Unique identifier for the server.
            server_info: Server information dictionary.
            save_path: Path to save the registry to. If None, uses ~/.mcp/custom_registry.json.
            
        Returns:
            Tuple of (success, output).
        """
        save_path = save_path or os.path.expanduser("~/.mcp/custom_registry.json")
        
        try:
            # Load existing registry if it exists
            existing_registry = {"servers": {}}
            if os.path.exists(save_path):
                with open(save_path, 'r') as f:
                    existing_registry = json.load(f)
            
            # Add or update the server entry
            if "servers" not in existing_registry:
                existing_registry["servers"] = {}
            
            existing_registry["servers"][server_id] = server_info
            
            # Save the registry
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(existing_registry, f, indent=2)
            
            # Update our registry
            if not self.registry_path:
                self.registry_path = save_path
            
            self.refresh_registry()
            
            return True, f"Added server '{server_id}' to custom registry at {save_path}"
        
        except Exception as e:
            logger.error(f"Error creating custom registry entry: {e}")
            return False, f"Error creating custom registry entry: {str(e)}"


# Example usage
if __name__ == "__main__":
    installer = MCPServerInstaller()
    
    # List available servers
    available_servers = installer.get_available_servers()
    print(f"Found {len(available_servers)} available servers in registry:")
    for server_id, info in available_servers.items():
        print(f"  - {server_id}: {info.get('name', 'Unnamed')} ({info.get('description', 'No description')})")
    
    # Install a server
    if available_servers:
        test_server_id = next(iter(available_servers.keys()))
        success, output, config = installer.install_server(test_server_id)
        if success:
            print(f"Successfully installed server '{test_server_id}'")
            print(f"Configuration: {json.dumps(config, indent=2)}")
        else:
            print(f"Failed to install server: {output}")
