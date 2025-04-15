"""
Plugin Example

This script demonstrates the usage of the plugin system in the MCP Router.
"""

import os
import sys
import asyncio
import logging
import json
from typing import Dict, List, Any

# Add the examples directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_router.core.router.mcp_router_enhanced import MCPRouterEnhanced
from examples.plugins.example_plugin import ExamplePlugin
from examples.plugins.keyword_routing_plugin import KeywordRoutingPlugin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
)

async def main():
    """Main function to demonstrate the plugin system."""
    # Create the enhanced MCP Router
    router = MCPRouterEnhanced(
        # Use environment variables for API keys
        openrouter_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        
        # Enable disk caching
        use_disk_cache=True,
        memory_cache_size=1000,
        disk_cache_size=10000,
        
        # Health check interval in seconds
        health_check_interval=60,
        
        # Plugin directories
        plugin_dirs=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")]
    )
    
    # Initialize the router
    await router.initialize()
    
    try:
        # Register a server
        router.register_server(
            "filesystem",
            {
                "name": "Filesystem MCP Server",
                "description": "Provides access to the local filesystem",
                "server_type": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", "."],
            },
            ["filesystem", "file_read", "file_write", "file_search"]
        )
        
        # Register another server
        router.register_server(
            "search",
            {
                "name": "Search MCP Server",
                "description": "Provides search capabilities",
                "server_type": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-search"],
            },
            ["search", "web_search", "image_search"]
        )
        
        # Wait for servers to initialize
        await asyncio.sleep(2)
        
        # Get plugins
        print("\n=== Plugins ===")
        plugins = router.get_all_plugins()
        print(f"Loaded Plugins: {list(plugins.keys())}")
        
        # Route a request
        print("\n=== Routing Request ===")
        result = await router.route_request("I need to read a file from my filesystem")
        print(f"Selected Servers: {result['selected_servers']}")
        print(f"Routing Confidence: {result['routing_confidence']}")
        
        # Route another request
        print("\n=== Routing Request ===")
        result = await router.route_request("I need to search for information on the web")
        print(f"Selected Servers: {result['selected_servers']}")
        print(f"Routing Confidence: {result['routing_confidence']}")
        
        # Route a request with no clear match
        print("\n=== Routing Request (No Clear Match) ===")
        result = await router.route_request("What is the weather like today?")
        print(f"Selected Servers: {result['selected_servers']}")
        print(f"Routing Confidence: {result['routing_confidence']}")
        
    finally:
        # Shutdown the router
        await router.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
