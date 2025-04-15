"""
Example Plugin

This is an example plugin for the MCP Router system.
"""

import logging
from typing import Dict, List, Any, Optional

from mcp_router.core.plugins.plugin_interface import RouterExtensionPlugin

logger = logging.getLogger(__name__)

class ExamplePlugin(RouterExtensionPlugin):
    """
    Example plugin that logs user queries.
    """
    
    def __init__(self):
        """
        Initialize the example plugin.
        """
        self.router = None
        self.query_count = 0
    
    async def initialize(self, router: Any) -> bool:
        """
        Initialize the plugin.
        
        Args:
            router: Reference to the MCPRouter instance
            
        Returns:
            True if initialization was successful, False otherwise
        """
        logger.info("Initializing example plugin")
        self.router = router
        return True
    
    async def shutdown(self) -> None:
        """
        Shutdown the plugin.
        """
        logger.info(f"Shutting down example plugin, processed {self.query_count} queries")
    
    def get_name(self) -> str:
        """
        Get the name of the plugin.
        
        Returns:
            String name of the plugin
        """
        return "example_plugin"
    
    def get_version(self) -> str:
        """
        Get the version of the plugin.
        
        Returns:
            String version of the plugin (semver format)
        """
        return "1.0.0"
    
    def get_description(self) -> str:
        """
        Get the description of the plugin.
        
        Returns:
            String description of the plugin
        """
        return "Example plugin that logs user queries"
    
    async def handle_request(self, user_query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle a user request.
        
        Args:
            user_query: The user's query
            context: Dictionary containing context information
            
        Returns:
            Optional dictionary containing handling result or None to continue normal processing
        """
        self.query_count += 1
        logger.info(f"Example plugin processing query: {user_query}")
        
        # Just log the query and continue normal processing
        return None
