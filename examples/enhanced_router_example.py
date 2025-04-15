"""
Enhanced MCP Router Example

This script demonstrates the usage of the enhanced MCP Router with
the plugin system, adapter framework, and caching system.
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Any

from mcp_router.core.router.mcp_router_enhanced import MCPRouterEnhanced

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
)

async def main():
    """Main function to demonstrate the enhanced MCP Router."""
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
        health_check_interval=60
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
        
        # Route a request
        print("\n=== Routing Request ===")
        result = await router.route_request("I need to read a file from my filesystem")
        print(f"Selected Servers: {result['selected_servers']}")
        print(f"Routing Confidence: {result['routing_confidence']}")
        
        # Route another request (should use cache)
        print("\n=== Routing Request (Cached) ===")
        result = await router.route_request("I need to read a file from my filesystem")
        print(f"Selected Servers: {result['selected_servers']}")
        print(f"Routing Confidence: {result['routing_confidence']}")
        
        # Get cache statistics
        print("\n=== Cache Statistics ===")
        cache_stats = await router.get_cache_stats()
        print(json.dumps(cache_stats, indent=2))
        
        # Get server health
        print("\n=== Server Health ===")
        health = await router.get_all_server_health()
        print(json.dumps(health, indent=2))
        
        # Get adapters
        print("\n=== Adapters ===")
        adapters = router.get_all_adapters()
        print(f"Loaded Adapters: {list(adapters.keys())}")
        
        # Get plugins
        print("\n=== Plugins ===")
        plugins = router.get_all_plugins()
        print(f"Loaded Plugins: {list(plugins.keys())}")
        
    finally:
        # Shutdown the router
        await router.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
