# MCP Router

A robust system for managing and routing requests to hundreds of MCP servers efficiently.

## Features

- **Server Registry**: Manage hundreds of MCP servers with metadata about their capabilities
- **Metadata Store**: Persistent storage for server metadata and usage statistics
- **Intelligent Router**: LLM-powered query analysis and server selection
- **Health Monitoring**: Automatic health checks and status tracking for all servers

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Router System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────┐        ┌───────────────────────────┐    │
│  │  Server Registry  │◄───────┤ Intelligent Router        │    │
│  │                   │        │                           │    │
│  └───────────┬───────┘        └───────────────┬───────────┘    │
│              │                                │                 │
│              ▼                                ▼                 │
│  ┌───────────────────┐        ┌───────────────────────────┐    │
│  │  Metadata Store   │◄───────┤ Tool Orchestrator         │    │
│  │                   │        │                           │    │
│  └───────────┬───────┘        └───────────────┬───────────┘    │
│              │                                │                 │
│              ▼                                ▼                 │
│  ┌───────────────────────────────────────────────────────┐     │
│  │                Health Monitoring System                │     │
│  │                                                        │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Server Network                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Code Index  │  │ Knowledge   │  │ File System │  ...        │
│  │ MCP Server  │  │ DB Server   │  │ MCP Server  │             │
│  │             │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/Sequencer.git
cd Sequencer

# Install the package
pip install -e .

# Install optional dependencies
pip install -e ".[openai,anthropic]"
```

## Usage

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

See the `examples` directory for more examples.

## Components

### Server Registry

The `ServerRegistry` class manages the registration, discovery, and status tracking of MCP servers in the system. It provides methods for:

- Registering and unregistering servers
- Getting servers by capability
- Updating server health status
- Tracking server capabilities

### Metadata Store

The `MetadataStore` class provides a SQLite-based storage system for MCP server metadata, allowing for efficient storage and retrieval of server information. It provides methods for:

- Storing and retrieving server metadata
- Finding servers for specific tasks
- Recording server usage statistics
- Managing server tags and capabilities

### Intelligent Router

The `IntelligentRouter` class analyzes user queries and determines the most appropriate MCP servers to handle them based on capabilities and metadata. It provides methods for:

- Analyzing queries using LLMs (OpenAI, Anthropic, OpenRouter)
- Selecting servers based on query analysis
- Matching query requirements to server capabilities

### Health Monitor

The `HealthMonitor` class provides functionality to monitor the health of MCP servers and update their status in the registry. It provides methods for:

- Checking server health
- Monitoring server status over time
- Tracking response times and error rates

## License

MIT
