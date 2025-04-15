"""
Server Registry Module

This module provides a registry for MCP servers, allowing the system to track
and manage hundreds of MCP servers efficiently.
"""

import os
import time
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class ServerRegistry:
    """
    Registry for MCP servers with metadata about their capabilities.
    
    This class manages the registration, discovery, and status tracking
    of MCP servers in the system.
    """
    
    def __init__(self, registry_file: Optional[str] = None):
        """
        Initialize the server registry.
        
        Args:
            registry_file: Optional path to a JSON file for persistent storage
        """
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.server_capabilities: Dict[str, Set[str]] = {}
        self.server_health: Dict[str, Dict[str, Any]] = {}
        self.registry_file = registry_file or os.path.expanduser("~/.mcp_router/server_registry.json")
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load the server registry from disk if it exists."""
        registry_path = Path(self.registry_file)
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    data = json.load(f)
                    self.servers = data.get('servers', {})
                    
                    # Convert capabilities from lists to sets
                    self.server_capabilities = {
                        server_id: set(capabilities) 
                        for server_id, capabilities in data.get('server_capabilities', {}).items()
                    }
                    
                    self.server_health = data.get('server_health', {})
                logger.info(f"Loaded {len(self.servers)} servers from registry")
            except Exception as e:
                logger.error(f"Error loading server registry: {e}")
                # Initialize with empty data
                self.servers = {}
                self.server_capabilities = {}
                self.server_health = {}
        else:
            logger.info("No existing registry found, starting with empty registry")
            # Ensure the directory exists
            os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    
    def _save_registry(self) -> None:
        """Save the server registry to disk."""
        try:
            # Convert capabilities from sets to lists for JSON serialization
            serializable_capabilities = {
                server_id: list(capabilities)
                for server_id, capabilities in self.server_capabilities.items()
            }
            
            data = {
                'servers': self.servers,
                'server_capabilities': serializable_capabilities,
                'server_health': self.server_health
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.servers)} servers to registry")
        except Exception as e:
            logger.error(f"Error saving server registry: {e}")
    
    def register_server(self, 
                       server_id: str, 
                       server_config: Dict[str, Any], 
                       capabilities: Optional[List[str]] = None) -> None:
        """
        Register a new MCP server with metadata about its capabilities.
        
        Args:
            server_id: Unique identifier for the server
            server_config: Configuration for the server
            capabilities: List of capabilities provided by the server
        """
        self.servers[server_id] = server_config
        
        if capabilities:
            self.server_capabilities[server_id] = set(capabilities)
        elif server_id not in self.server_capabilities:
            self.server_capabilities[server_id] = set()
        
        self.server_health[server_id] = {
            "status": "online",
            "last_check": time.time(),
            "last_successful_connection": time.time(),
            "error_count": 0,
            "average_response_time": 0.0
        }
        
        self._save_registry()
        logger.info(f"Registered server: {server_id}")
    
    def unregister_server(self, server_id: str) -> bool:
        """
        Remove a server from the registry.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            True if the server was found and removed, False otherwise
        """
        if server_id in self.servers:
            del self.servers[server_id]
            
            if server_id in self.server_capabilities:
                del self.server_capabilities[server_id]
            
            if server_id in self.server_health:
                del self.server_health[server_id]
            
            self._save_registry()
            logger.info(f"Unregistered server: {server_id}")
            return True
        
        logger.warning(f"Attempted to unregister unknown server: {server_id}")
        return False
    
    def get_server_config(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            Server configuration or None if not found
        """
        return self.servers.get(server_id)
    
    def get_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered servers.
        
        Returns:
            Dictionary of server_id to server configuration
        """
        return self.servers
    
    def get_servers_by_capability(self, capability: str) -> List[str]:
        """
        Find all servers that support a specific capability.
        
        Args:
            capability: The capability to search for
            
        Returns:
            List of server IDs that support the capability
        """
        return [
            server_id 
            for server_id, capabilities in self.server_capabilities.items()
            if capability in capabilities and 
               self.server_health.get(server_id, {}).get("status") == "online"
        ]
    
    def get_servers_by_capabilities(self, capabilities: List[str], require_all: bool = True) -> List[str]:
        """
        Find servers that support the specified capabilities.
        
        Args:
            capabilities: List of capabilities to search for
            require_all: If True, servers must support all capabilities; if False, any capability
            
        Returns:
            List of server IDs that support the capabilities
        """
        if not capabilities:
            return list(self.servers.keys())
        
        capability_set = set(capabilities)
        
        if require_all:
            # Servers must support all capabilities
            return [
                server_id 
                for server_id, server_capabilities in self.server_capabilities.items()
                if capability_set.issubset(server_capabilities) and
                   self.server_health.get(server_id, {}).get("status") == "online"
            ]
        else:
            # Servers must support any capability
            return [
                server_id 
                for server_id, server_capabilities in self.server_capabilities.items()
                if capability_set.intersection(server_capabilities) and
                   self.server_health.get(server_id, {}).get("status") == "online"
            ]
    
    def update_server_capabilities(self, server_id: str, capabilities: List[str]) -> bool:
        """
        Update the capabilities of a server.
        
        Args:
            server_id: Unique identifier for the server
            capabilities: New list of capabilities
            
        Returns:
            True if the server was found and updated, False otherwise
        """
        if server_id in self.servers:
            self.server_capabilities[server_id] = set(capabilities)
            self._save_registry()
            logger.info(f"Updated capabilities for server: {server_id}")
            return True
        
        logger.warning(f"Attempted to update capabilities for unknown server: {server_id}")
        return False
    
    def update_server_health(self, server_id: str, status: str, response_time: Optional[float] = None) -> bool:
        """
        Update the health status of a server.
        
        Args:
            server_id: Unique identifier for the server
            status: New status ("online", "offline", "error")
            response_time: Optional response time in seconds
            
        Returns:
            True if the server was found and updated, False otherwise
        """
        if server_id in self.servers:
            now = time.time()
            
            if server_id not in self.server_health:
                self.server_health[server_id] = {
                    "status": status,
                    "last_check": now,
                    "last_successful_connection": now if status == "online" else 0,
                    "error_count": 0 if status == "online" else 1,
                    "average_response_time": response_time or 0.0
                }
            else:
                health = self.server_health[server_id]
                health["status"] = status
                health["last_check"] = now
                
                if status == "online":
                    health["last_successful_connection"] = now
                    health["error_count"] = 0
                else:
                    health["error_count"] += 1
                
                if response_time is not None:
                    # Update average response time with exponential moving average
                    alpha = 0.3  # Weight for new value
                    old_avg = health.get("average_response_time", 0.0)
                    health["average_response_time"] = (alpha * response_time) + ((1 - alpha) * old_avg)
            
            self._save_registry()
            logger.info(f"Updated health for server: {server_id} to {status}")
            return True
        
        logger.warning(f"Attempted to update health for unknown server: {server_id}")
        return False
    
    def get_server_health(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the health status of a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            Health status dictionary or None if not found
        """
        return self.server_health.get(server_id)
    
    def get_all_server_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status for all servers.
        
        Returns:
            Dictionary of server_id to health status
        """
        return self.server_health
    
    def get_online_servers(self) -> List[str]:
        """
        Get all servers that are currently online.
        
        Returns:
            List of server IDs that are online
        """
        return [
            server_id
            for server_id, health in self.server_health.items()
            if health.get("status") == "online"
        ]
    
    def get_offline_servers(self) -> List[str]:
        """
        Get all servers that are currently offline.
        
        Returns:
            List of server IDs that are offline
        """
        return [
            server_id
            for server_id, health in self.server_health.items()
            if health.get("status") != "online"
        ]
