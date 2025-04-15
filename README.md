# MCP Router

A powerful router for MCP (Model Context Protocol) queries with plugin system, adapter framework, and caching.

## Features

- **Dynamic Plugin System**: Easily extend the router's functionality with plugins
- **MCP Adapter Framework**: Support for different types of MCP servers
- **Advanced Caching System**: Multi-level caching with memory and disk storage
- **Intelligent Routing**: Route queries to the most appropriate MCP servers
- **Health Monitoring**: Monitor the health of MCP servers
- **Metadata Storage**: Store and retrieve metadata about MCP servers

## Installation

```bash
# Install from source
git clone https://github.com/Zeeeepa/mcp-router.git
cd mcp-router
pip install -e .

# Install with MCP SDK support
pip install -e ".[mcp]"
```

## Usage

### Basic Usage

```python
import asyncio
from mcp_router import MCPRouter

async def main():
    # Create the MCP Router
    router = MCPRouter()
    
    # Initialize the router
    await router.initialize()
    
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
    
    # Route a request
    result = await router.route_request("I need to read a file from my filesystem")
    print(f"Selected Servers: {result['selected_servers']}")
    
    # Shutdown the router
    await router.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Enhanced Usage

```python
import asyncio
from mcp_router import MCPRouterEnhanced

async def main():
    # Create the enhanced MCP Router
    router = MCPRouterEnhanced(
        # Enable disk caching
        use_disk_cache=True,
        memory_cache_size=1000,
        disk_cache_size=10000,
    )
    
    # Initialize the router
    await router.initialize()
    
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
    
    # Route a request
    result = await router.route_request("I need to read a file from my filesystem")
    print(f"Selected Servers: {result['selected_servers']}")
    
    # Execute a tool
    result = await router.execute_tool("filesystem", "readFile", {"path": "README.md"})
    print(f"File Contents: {result}")
    
    # Get cache statistics
    cache_stats = await router.get_cache_stats()
    print(f"Cache Stats: {cache_stats}")
    
    # Shutdown the router
    await router.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Components

### Dynamic Plugin System

The plugin system allows you to extend the router's functionality with custom plugins. Plugins can add new methods to the router, modify the behavior of existing methods, or add support for new types of MCP servers.

### MCP Adapter Framework

The adapter framework allows the router to interact with different types of MCP servers. Adapters provide a unified interface for connecting to servers, executing tools, and checking server health.

### Advanced Caching System

The caching system provides efficient storage and retrieval of data with support for multi-level caching. It includes memory and disk caching with optional expiration and invalidation.

### Intelligent Routing

The intelligent router analyzes user queries and determines the most appropriate MCP servers to handle them. It uses LLMs (Language Model Models) to analyze queries and match them to server capabilities.

### Health Monitoring

The health monitor tracks the health of MCP servers and updates their status in the registry. It periodically checks server health and provides statistics on server performance.

### Metadata Storage

The metadata store provides persistent storage for server metadata, allowing for efficient storage and retrieval of server information.

## License

MIT
