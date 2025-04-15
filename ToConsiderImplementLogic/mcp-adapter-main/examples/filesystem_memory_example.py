"""
Filesystem and Memory Example

This example demonstrates using both Filesystem and Memory MCP servers with Gemini:
1. Creating and reading a file
2. Creating a memory node with information about the file
3. Searching for the memory node

This showcases:
- Integration of multiple MCP servers
- Using Gemini for LLM inference
- Knowledge graph operations
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Third-party imports
from dotenv import load_dotenv
from mcp import StdioServerParameters

# Local imports
from src.llm import GeminiAdapter
from src.core import MCPClient, MCPTools

load_dotenv()

async def main() -> None:
    """
    Run the filesystem and memory integration example.
    
    Demonstrates how to:
    1. Create and read files
    2. Create memory nodes with metadata
    3. Search memory for stored information
    """
    # Setup logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Setup parameters
    desktop_path = os.getenv('DESKTOP_PATH')
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not desktop_path or not api_key:
        print("ERROR: Both DESKTOP_PATH and GEMINI_API_KEY must be set in .env file")
        return
    
    # Configure the Filesystem MCP server
    fs_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", desktop_path],
        env=None
    )

    # Configure the Memory MCP server
    mem_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-memory"],
        env=None
    )

    # Initialize MCP clients for filesystem and memory
    fs_client = MCPClient(
        fs_params,        
        debug=True,
        log_file=log_dir / "filesystem_client.log",
        client_name="fs_client"
    )
    
    mem_client = MCPClient(
        mem_params,
        debug=True,
        log_file=log_dir / "memory_client.log",
        client_name="mem_client"
    )

    # Initialize our Gemini adapter (LLM client)
    llm_client = GeminiAdapter(
        model_name='gemini-1.5-flash',
        debug=True,
        log_file=log_dir / "gemini_adapter.log"
    )

    try:
        # Get tools from both servers
        fs_tools = await fs_client.get_tools()
        mem_tools = await mem_client.get_tools()
        
        # Create MCPTools instance and add tools
        tools = MCPTools()
        tools.add(fs_tools)
        tools.add(mem_tools)

        # Setup the pipeline
        await llm_client.prepare_tools(tools)
        await llm_client.configure(api_key)

        # 1) Create a file in the desktop directory
        print("\n=== Creating File ===")
        create_file_prompt = (
            f"Create a file called test-mcp-adapter-example.txt "
            f"with text 'This is a test for the MCP adapter example!' "
            f"in path: {desktop_path}"
        )
        response = await llm_client.send_message(create_file_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            create_file_result = await fs_client.execute_tool(tool_name, tool_args)
            print("Create file result:", create_file_result)
        else:
            print("Failed to extract tool call for file creation")
            return

        # 2) Read the file content and print it
        print("\n=== Reading File Content ===")
        read_file_prompt = f"Read the file test-mcp-adapter-example.txt from path: {desktop_path}"
        response = await llm_client.send_message(read_file_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            file_content = await fs_client.execute_tool(tool_name, tool_args)
            print("File content:", file_content)
        else:
            print("Failed to extract tool call for file reading")
            return

        # 3) Create a new "test-mcp-adapter-example" node in memory with text & path
        print("\n=== Creating Memory Node ===")
        create_node_prompt = (
            "Create a new memory node named 'test-mcp-adapter-example' that stores "
            f"information about the file at {desktop_path}/test-mcp-adapter-example.txt "
            "and what it contains."
        )
        response = await llm_client.send_message(create_node_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            node_creation_result = await mem_client.execute_tool(tool_name, tool_args)
            print("Memory node creation result:", node_creation_result)
        else:
            print("Failed to extract tool call for memory node creation")
            return

        # 4) Search for 'mcp-adapter-example' node and print the found result
        print("\n=== Searching for 'mcp-adapter-example' Node ===")
        search_node_prompt = "Search for memory nodes that match the name 'mcp-adapter-example'"
        response = await llm_client.send_message(search_node_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            search_result = await mem_client.execute_tool(tool_name, tool_args)
            print("Search result:", search_result)
        else:
            print("Failed to extract tool call for memory search")
        
        # Log completion status
        fs_client.logger.end_session("completed")
        mem_client.logger.end_session("completed")
        llm_client.logger.end_session("completed")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        fs_client.logger.end_session("failed")
        mem_client.logger.end_session("failed")
        llm_client.logger.end_session("failed")
    finally:
        # Always close clients
        await fs_client.close()
        await mem_client.close()
        # No need to close LLM adapter as it doesn't maintain a persistent connection

if __name__ == "__main__":
    asyncio.run(main())