"""
Keyword Routing Plugin

This plugin implements a simple keyword-based routing strategy.
"""

import logging
import re
from typing import Dict, List, Any, Optional

from mcp_router.core.plugins.plugin_interface import RoutingStrategyPlugin

logger = logging.getLogger(__name__)

class KeywordRoutingPlugin(RoutingStrategyPlugin):
    """
    Plugin that implements a simple keyword-based routing strategy.
    """
    
    def __init__(self):
        """
        Initialize the keyword routing plugin.
        """
        self.router = None
        self.confidence_score = 0.0
        self.keyword_map = {
            r'\b(file|read|write|directory|folder|path)\b': ['filesystem'],
            r'\b(search|find|lookup|query)\b': ['search'],
            r'\b(image|picture|photo|draw|render)\b': ['image'],
            r'\b(code|program|function|class|method)\b': ['code'],
            r'\b(database|sql|query|table|record)\b': ['database'],
        }
    
    async def initialize(self, router: Any) -> bool:
        """
        Initialize the plugin.
        
        Args:
            router: Reference to the MCPRouter instance
            
        Returns:
            True if initialization was successful, False otherwise
        """
        logger.info("Initializing keyword routing plugin")
        self.router = router
        return True
    
    async def shutdown(self) -> None:
        """
        Shutdown the plugin.
        """
        logger.info("Shutting down keyword routing plugin")
    
    def get_name(self) -> str:
        """
        Get the name of the plugin.
        
        Returns:
            String name of the plugin
        """
        return "keyword_routing_plugin"
    
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
        return "Plugin that implements a simple keyword-based routing strategy"
    
    async def select_servers(self, user_query: str, available_servers: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Select servers for a user query.
        
        Args:
            user_query: The user's query
            available_servers: Dictionary of server_id to server configuration
            
        Returns:
            List of server IDs to route the query to
        """
        logger.info(f"Selecting servers for query: {user_query}")
        
        # Convert query to lowercase
        query_lower = user_query.lower()
        
        # Match keywords
        matched_servers = set()
        match_count = 0
        total_patterns = len(self.keyword_map)
        
        for pattern, servers in self.keyword_map.items():
            if re.search(pattern, query_lower):
                match_count += 1
                for server in servers:
                    if server in available_servers:
                        matched_servers.add(server)
        
        # Calculate confidence score
        if match_count > 0:
            self.confidence_score = min(1.0, match_count / total_patterns + 0.3)
        else:
            self.confidence_score = 0.0
        
        # If no servers matched, return all available servers
        if not matched_servers:
            logger.info("No servers matched, returning all available servers")
            self.confidence_score = 0.1
            return list(available_servers.keys())
        
        logger.info(f"Selected servers: {matched_servers}")
        return list(matched_servers)
    
    def get_confidence_score(self) -> float:
        """
        Get the confidence score for the last routing decision.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        return self.confidence_score
