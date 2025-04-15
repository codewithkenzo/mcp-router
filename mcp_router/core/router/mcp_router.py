"""
MCP Router Module

This module provides the main router for MCP queries, integrating
the server registry, metadata store, intelligent router, and health monitor.
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

logger = logging.getLogger(__name__)

class MCPRouter:
    """
    Main router for MCP queries.
    
    This class integrates the server registry, metadata store,
    intelligent router, and health monitor to provide a complete
    routing solution for MCP queries.
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 registry_file: Optional[str] = None,
                 db_path: Optional[str] = None,
                 openrouter_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None,
                 health_check_interval: int = 300):
        """
        Initialize the MCP router.
        
        Args:
            config_path: Optional path to a configuration file
            registry_file: Optional path to a registry file
            db_path: Optional path to a database file
            openrouter_api_key: Optional API key for OpenRouter
            openai_api_key: Optional API key for OpenAI
            anthropic_api_key: Optional API key for Anthropic
            health_check_interval: Interval between health checks in seconds
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
        logger.info("Initializing MCP Router")
        
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
        
        # Start health monitoring
        await self.health_monitor.start_monitoring()
        
        logger.info("MCP Router initialized")
    
    async def shutdown(self):
        """Shutdown the router and its components."""
        logger.info("Shutting down MCP Router")
        
        # Stop health monitoring
        await self.health_monitor.stop_monitoring()
        
        logger.info("MCP Router shut down")
    
    async def route_request(self, user_query: str) -> Dict[str, Any]:
        """
        Route a user request to appropriate MCP servers.
        
        Args:
            user_query: The user's query
            
        Returns:
            Dictionary containing routing information
        """
        logger.info(f"Routing request: {user_query}")
        
        # Select servers based on the query
        selected_servers = await self.intelligent_router.select_servers(user_query)
        
        if not selected_servers:
            logger.warning("No suitable MCP servers found for this query")
            return {
                "query": user_query,
                "selected_servers": [],
                "routing_confidence": 0.0,
                "error": "No suitable MCP servers found for this query"
            }
        
        # Store routing decision
        self.last_routing_decision = {
            "query": user_query,
            "selected_servers": selected_servers,
            "routing_confidence": self.intelligent_router.get_confidence_score(),
            "timestamp": time.time()
        }
        
        logger.info(f"Selected servers: {selected_servers}")
        
        return {
            "query": user_query,
            "selected_servers": selected_servers,
            "routing_confidence": self.intelligent_router.get_confidence_score()
        }
    
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
            
            logger.info(f"Registered server: {server_id}")
            return True
        except Exception as e:
            logger.error(f"Error registering server: {e}")
            return False
    
    def unregister_server(self, server_id: str) -> bool:
        """
        Unregister a server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            True if successful, False otherwise
        """
        try:
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
