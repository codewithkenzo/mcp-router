"""
Filesystem Example

This example demonstrates using the Filesystem MCP server with OpenAI:
1. Creating a file on the desktop
2. Listing the contents of a directory

This showcases:
- Integration with Filesystem MCP server
- Basic file operations via MCP
- Tool call validation
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Third-party imports
from dotenv import load_dotenv
from mcp import StdioServerParameters

# Local imports
from src.llm import OpenAIAdapter
from src.core import MCPClient, MCPTools

load_dotenv()

async def main() -> None:
    """
    Run the filesystem example.
    
    Demonstrates how to:
    1. Create a file on the desktop
    2. List directory contents
    """
    # Setup logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Setup parameters
    desktop_path = os.getenv('DESKTOP_PATH')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not desktop_path or not api_key:
        print("ERROR: Both DESKTOP_PATH and OPENAI_API_KEY must be set in .env file")
        return
    
    # Configure MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", desktop_path],
        env=None
    )

    # Initialize clients with logging enabled
    mcp_client = MCPClient(
        server_params,
        debug=True,  # Enable debug logging
        log_file=log_dir / "filesystem_client.log",
        client_name="fs_client"
    )
    
    llm_client = OpenAIAdapter(
        model_name='gpt-4o-mini',
        debug=True,  # Enable debug logging
        log_file=log_dir / "openai_adapter.log"
    )

    try:
        # Setup the pipeline
        raw_tools = await mcp_client.get_tools()
        tools = MCPTools()
        tools.add(raw_tools)
        
        await llm_client.prepare_tools(tools)
        await llm_client.configure(api_key)

        # Example 1: Create a file
        print("\n=== Creating File ===")
        message = f"Create a file called hello.txt with content 'Hello from MCP!' in path: {desktop_path}"
        response = await llm_client.send_message(message)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            result = await mcp_client.execute_tool(tool_name, tool_args)
            print("Create file result:", result)
        else:
            print("Failed to extract tool call for file creation")
            return

        # Example 2: List directory
        print("\n=== Listing Directory Contents ===")
        message = f"List the contents of {desktop_path}"
        response = await llm_client.send_message(message)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            result = await mcp_client.execute_tool(tool_name, tool_args)
            print("Directory contents:", result)
        else:
            print("Failed to extract tool call for directory listing")

        # Log completion status
        mcp_client.logger.end_session("completed")
        llm_client.logger.end_session("completed")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        mcp_client.logger.end_session("failed")
        llm_client.logger.end_session("failed")
    finally:
        # Always close clients
        await mcp_client.close()
        # No need to close LLM adapter as it doesn't maintain a persistent connection

if __name__ == "__main__":
    asyncio.run(main())