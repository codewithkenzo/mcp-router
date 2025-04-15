#!/usr/bin/env python3
"""
MCP Router Example

This script demonstrates how to use the MCP Router to manage and route
requests to MCP servers.
"""

import os
import sys
import asyncio
import json
import logging
from typing import Dict, List, Any

# Add the parent directory to the path so we can import the mcp_router package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_router import MCPRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample server configurations
SAMPLE_SERVERS = {
    "filesystem": {
        "name": "Filesystem MCP Server",
        "description": "Provides access to the local filesystem",
        "server_type": "stdio",
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem", "."],
        "capabilities": ["filesystem", "file_read", "file_write", "file_search"],
        "tags": ["filesystem", "local"]
    },
    "search": {
        "name": "Search MCP Server",
        "description": "Provides web search capabilities",
        "server_type": "stdio",
        "command": "npx",
        "args": ["search-mcp-server"],
        "capabilities": ["web_search", "image_search", "news_search"],
        "tags": ["search", "web"]
    },
    "code": {
        "name": "Code MCP Server",
        "description": "Provides code analysis and generation capabilities",
        "server_type": "stdio",
        "command": "npx",
        "args": ["code-mcp-server"],
        "capabilities": ["code_analysis", "code_generation", "code_search"],
        "tags": ["code", "development"]
    }
}

async def main():
    """Main function to demonstrate the MCP Router."""
    # Create the MCP Router
    router = MCPRouter()
    
    # Initialize the router
    await router.initialize()
    
    # Register sample servers
    for server_id, server_config in SAMPLE_SERVERS.items():
        router.register_server(
            server_id,
            server_config,
            server_config.get("capabilities", [])
        )
    
    # Print registered servers
    print("\nRegistered Servers:")
    for server_id, server_config in router.server_registry.get_all_servers().items():
        print(f"- {server_id}: {server_config.get('name', server_id)}")
    
    # Print all capabilities
    print("\nAll Capabilities:")
    all_capabilities = set()
    for server_id, capabilities in router.server_registry.server_capabilities.items():
        all_capabilities.update(capabilities)
    for capability in sorted(all_capabilities):
        print(f"- {capability}")
    
    # Test routing some queries
    test_queries = [
        "I need to search for information about climate change",
        "Can you help me analyze this Python code?",
        "I need to read a file from my filesystem",
        "What's the weather like today?",
        "Generate a React component for a login form"
    ]
    
    print("\nRouting Test Queries:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = await router.route_request(query)
        print(f"Selected Servers: {result['selected_servers']}")
        print(f"Confidence: {result['routing_confidence']:.2f}")
    
    # Check server health
    print("\nServer Health:")
    for server_id in router.server_registry.get_all_servers().keys():
        await router.check_server_health(server_id)
    
    health_status = await router.get_all_server_health()
    for server_id, status in health_status.items():
        print(f"- {server_id}: {status.get('status', 'unknown')}")
    
    # Shutdown the router
    await router.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
