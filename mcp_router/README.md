# MCP Router

A Python library for interacting with Model Context Protocol (MCP) servers with OpenRouter LLM integration.

## Features

- **Modular Architecture**: Clean separation of concerns with provider-specific modules
- **Dual Interface**: Use as a Python library or command-line tool
- **MCP Server Integration**: Connect to any number of MCP servers simultaneously
- **OpenRouter Integration**: Seamless access to AI models through OpenRouter
- **Server Management**: Install, start, stop, and manage MCP servers
- **Flexible Configuration**: Support for local and remote server registries

## Core Components

- **core/openrouter.py**: OpenRouter API client for LLM integration
- **core/server_manager.py**: MCP server management and communication
- **server_management/**: Tools for installing, configuring, and managing MCP servers
- **utils/**: Utility functions and helper classes
- **cli/**: Command-line interface

## Usage

```python
from mcp_router import MCPRouter

# Initialize the router
router = MCPRouter()

# Use the router to interact with MCP servers and OpenRouter
```

See the root README.md for full usage examples and documentation. 