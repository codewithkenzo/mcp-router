## What is MCP Adapter?

MCP Adapter is a Python package that bridges Large Language Models (LLMs) with the Model Context Protocol (MCP) ecosystem. It enables seamless integration between popular LLM providers (OpenAI, Gemini) and a variety of specialized MCP tools for file management, memory storage, APIs, and more.

**Why MCP Adapter?**

- **Standardized Tool Interaction**: Use a consistent interface to work with any MCP-compatible tool
- **Multi-tool Orchestration**: Coordinate multiple specialized services in one workflow
- **Simplified LLM Integration**: Connect powerful language models to real-world capabilities
- **Security by Design**: Benefit from MCP's isolated server architecture for better security boundaries
- **Learning Resource**: Excellent starting point for understanding tool-using AI workflows

MCP Adapter is perfect for developers who want to build AI applications that can interact with the real world while maintaining a clean separation of concerns.

## Architecture
The MCP Adapter architecture consists of three main components:

1. **MCP Client**: Manages connections to individual MCP servers and executes tool calls
2. **Tool Orchestrator**: Coordinates multiple MCP servers and routes tool calls to the appropriate service
3. **LLM Adapters**: Convert between LLM-specific formats and the MCP standard for tool definitions

## Installation

### Prerequisites

- Python 3.9+
- Node.js 16+ (for MCP servers)

### Installing from PyPI

```bash
pip install mcp-adapter
```

### Installing from source

```bash
git clone git@github.com:ToruGuy/mcp-adapter.git
cd mcp-adapter
pip install -e .
```

## Quick Start

### Environment Setup

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### Basic Example

```python
import asyncio
import os
from dotenv import load_dotenv
from mcp import StdioServerParameters
from mcp_adapter.core import MCPClient
from mcp_adapter.llm import OpenAIAdapter

# Load environment variables
load_dotenv()

async def main():
    # Configure a filesystem MCP server
    fs_params = StdioServerParameters(
        command="npx", 
        args=["-y", "@modelcontextprotocol/server-filesystem", "./data"]
    )
    
    # Initialize client
    fs_client = MCPClient(fs_params, client_name="filesystem")
    
    try:
        # Get available tools from server
        tools = await fs_client.get_tools()
        
        # Initialize LLM adapter
        llm = OpenAIAdapter(model_name="gpt-4o-mini")
        await llm.prepare_tools(tools)
        await llm.configure(os.getenv("OPENAI_API_KEY"))
        
        # Send a message to create a file
        response = await llm.send_message("Create a file called example.txt with content 'Hello, MCP!'")
        
        # Extract and execute tool call
        tool_name, tool_args = llm.extract_tool_call(response)
        if tool_name and tool_args:
            result = await fs_client.execute_tool(tool_name, tool_args)
            print(f"Tool execution result: {result}")
    finally:
        # Always close the client
        await fs_client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

### Working with Multiple MCP Servers

Orchestrate several MCP servers together with the `ToolOrchestrator`:

```python
from mcp_adapter.core import ToolOrchestrator

# Configure multiple server parameters
server_params = [fs_params, memory_params, time_params]

# Create orchestrator
orchestrator = ToolOrchestrator(server_params)

# Initialize all connections
await orchestrator.initialize()

# Execute tools (automatically routes to correct server)
result = await orchestrator.execute("read_file", {"path": "/path/to/file.txt"})

# Clean up when done
await orchestrator.close()
```

### Tool Validation

All tools are automatically validated against their JSON Schema before execution:

```python
# Validate tool parameters
is_valid, validation_errors = orchestrator.validate_tool_args("write_file", {
    "path": "/path/to/file.txt",
    "content": "File content here"
})

if is_valid:
    result = await orchestrator.execute("write_file", args)
else:
    print(f"Validation errors: {validation_errors}")
```

### Advanced LLM Integration

Support for function calling with OpenAI and Gemini:

```python
# For multi-turn conversations
conversation_id = "user-123"

# First user message
await llm.send_message("I need to create a todo list", conversation_id=conversation_id)

# LLM can suggest using tools
tool_response = await llm.send_message("Add 'Buy groceries' to my todo list", 
                                      conversation_id=conversation_id)

# Extract and execute tool calls
tool_name, tool_args = llm.extract_tool_call(tool_response)
if tool_name:
    result = await orchestrator.execute(tool_name, tool_args)
    
    # Send tool result back to LLM
    await llm.send_tool_result(result, conversation_id=conversation_id)
```

## Available MCP Servers

You can use MCP Adapter with a growing ecosystem of MCP servers:

| Server | Package | Description |
|--------|---------|-------------|
| Filesystem | `@modelcontextprotocol/server-filesystem` | File and directory operations |
| Memory | `@modelcontextprotocol/server-memory` | Knowledge graph storage |
| Time | `@modelcontextprotocol/server-time` | Time operations and scheduling |
| Redis | `@modelcontextprotocol/server-redis` | Key-value data storage |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | Database access |
| Git | `@modelcontextprotocol/server-git` | Git repository operations |
| GitHub | `@modelcontextprotocol/server-github` | GitHub API integration |
| Brave Search | `@modelcontextprotocol/server-brave-search` | Web search capabilities |

## Example Applications

The repository includes several example applications that demonstrate how to use MCP Adapter:

1. **[Filesystem Example](examples/filesystem_example.py)**: Basic file read/write operations
2. **[Time Example](examples/time_example.py)**: Working with timestamps and time-based calculations
3. **[Research Assistant](examples/research_assistant.py)**: A complete application combining filesystem and memory servers
4. **[Web Researcher](examples/web_researcher.py)**: Advanced research tool that searches the web, fetches content, and generates reports by combining Brave Search and Fetch servers

## Development and Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
./run_tests.sh

# Run specific test
python -m unittest tests.core.test_tools
```

## Security Best Practices

The MCP architecture provides strong security boundaries with isolated servers. To maintain security:

- Always validate user inputs before passing to tool execution
- Use environment variables for sensitive configuration
- Apply the principle of least privilege when configuring MCP servers
- Log all tool executions for audit purposes
- Keep MCP servers and dependencies updated

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <em>MCP Adapter: Building bridges between language models and real-world capabilities</em>
</p>
