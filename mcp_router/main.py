"""
MCP Router main module.
Provides the main interface for interacting with MCP servers and OpenRouter.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union, Set
import mcp
from dotenv import load_dotenv

from .core.openrouter import OpenRouterClient
from .core.server_manager import MCPServerManager
from .utils.playwright_utils import PlaywrightMCP
from .api import APIManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPRouter:
    """
    Main class for interacting with MCP servers and OpenRouter.
    Provides methods for installing and managing MCP servers, and using OpenRouter for LLM-based interactions.
    """
    
    def __init__(self, config_path: Optional[str] = None,
                 registry_path: Optional[str] = None,
                 openrouter_api_key: Optional[str] = None,
                 api_dir: Optional[str] = None):
        """
        Initialize the MCP Router.
        
        Args:
            config_path: Path to the MCP server config file.
            registry_path: Path to the MCP server registry file.
            openrouter_api_key: OpenRouter API key.
            api_dir: Path to the TypeScript API directory.
        """
        self.server_manager = MCPServerManager(config_path=config_path, registry_path=registry_path)
        self.openrouter_client = OpenRouterClient(api_key=openrouter_api_key)
        self.playwright_mcp = None
        self.mcp_client_initialized = False
        self.api_manager = APIManager(api_dir=api_dir)
    
    async def initialize(self, initialize_mcp_client: bool = True) -> None:
        """
        Initialize all components of the MCP Router.
        
        Args:
            initialize_mcp_client: Whether to initialize the MCP client.
        """
        # Initialize the server manager
        await self.server_manager.initialize()
        
        # Initialize the MCP client if requested
        if initialize_mcp_client:
            await self.initialize_mcp_client()
    
    async def initialize_mcp_client(self) -> None:
        """
        Initialize the MCP client.
        """
        if self.mcp_client_initialized:
            return
        
        # Initialize the Playwright MCP client
        self.playwright_mcp = PlaywrightMCP()
        await self.playwright_mcp.initialize()
        
        self.mcp_client_initialized = True
    
    async def get_available_providers(self) -> List[str]:
        """
        Get a list of available LLM providers.
        
        Returns:
            List[str]: A list of provider names.
        """
        return self.api_manager.get_available_providers()
    
    async def generate_text(self,
                     provider: str,
                     prompt: str,
                     system_prompt: Optional[str] = None,
                     model: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text using a specific provider.
        
        Args:
            provider: The provider name.
            prompt: The user prompt to generate text from.
            system_prompt: Optional system prompt to guide the generation.
            model: Optional model identifier to use for generation.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            
        Returns:
            Union[str, AsyncGenerator[str, None]]: Generated text or a stream of text chunks.
        """
        return await self.api_manager.generate_text(
            provider=provider,
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
    
    async def get_token_count(self, provider: str, text: str, model: Optional[str] = None) -> int:
        """
        Get the number of tokens in the given text for the specified model.
        
        Args:
            provider: The provider name.
            text: The text to count tokens for.
            model: Optional model identifier to use for token counting.
            
        Returns:
            int: The number of tokens in the text.
        """
        return await self.api_manager.get_token_count(provider, text, model)
    
    async def get_available_models(self, provider: str) -> List[Dict[str, Any]]:
        """
        Get a list of available models for a specific provider.
        
        Args:
            provider: The provider name.
            
        Returns:
            List[Dict[str, Any]]: A list of model information dictionaries.
        """
        return await self.api_manager.get_available_models(provider)
    
    async def list_available_servers(self) -> Dict[str, Any]:
        """
        List all available MCP servers in the registry.
        
        Returns:
            Dictionary of available servers.
        """
        return await self.server_manager.list_available_servers()
    
    async def list_configured_servers(self) -> Dict[str, Any]:
        """
        List all configured MCP servers.
        
        Returns:
            Dictionary of configured servers.
        """
        return await self.server_manager.list_configured_servers()
    
    async def list_running_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        List all running MCP servers.
        
        Returns:
            Dictionary of running server statuses.
        """
        return await self.server_manager.list_running_servers()
    
    async def install_server(self, server_id: str, config_overrides: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Install an MCP server.
        
        Args:
            server_id: Identifier of the server to install.
            config_overrides: Optional overrides for the server configuration.
            
        Returns:
            Tuple of (success, output, server_config).
        """
        return await self.server_manager.install_server(server_id, config_overrides)
    
    async def uninstall_server(self, server_id: str) -> Tuple[bool, str]:
        """
        Uninstall an MCP server.
        
        Args:
            server_id: Identifier of the server to uninstall.
            
        Returns:
            Tuple of (success, output).
        """
        return await self.server_manager.uninstall_server(server_id)
    
    async def start_server(self, server_id: str) -> Tuple[bool, Optional[str]]:
        """
        Start an MCP server.
        
        Args:
            server_id: Identifier of the server to start.
            
        Returns:
            Tuple of (success, error_message).
        """
        return await self.server_manager.start_server(server_id)
    
    async def stop_server(self, server_id: str, force: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Stop an MCP server.
        
        Args:
            server_id: Identifier of the server to stop.
            force: Whether to forcefully terminate the process.
            
        Returns:
            Tuple of (success, error_message).
        """
        return await self.server_manager.stop_server(server_id, force=force)
    
    async def restart_server(self, server_id: str) -> Tuple[bool, Optional[str]]:
        """
        Restart an MCP server.
        
        Args:
            server_id: Identifier of the server to restart.
            
        Returns:
            Tuple of (success, error_message).
        """
        return await self.server_manager.restart_server(server_id)
    
    async def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """
        Get the status of an MCP server.
        
        Args:
            server_id: Identifier of the server.
            
        Returns:
            Dictionary with status information.
        """
        return await self.server_manager.get_server_status(server_id)
    
    async def get_server_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """
        Get the tools provided by an MCP server.
        
        Args:
            server_id: Identifier of the server.
            
        Returns:
            List of tool definitions.
        """
        return await self.server_manager.get_server_tools(server_id)
    
    async def call_server_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on an MCP server.
        
        Args:
            server_id: Identifier of the server.
            tool_name: Name of the tool to call.
            arguments: Arguments for the tool.
            
        Returns:
            Result of the tool call.
        """
        return await self.server_manager.call_tool(server_id, tool_name, arguments)
    
    async def create_custom_server(self, server_id: str, command: str, args: List[str] = None, 
                                  env: Dict[str, str] = None) -> Tuple[bool, str]:
        """
        Create a custom MCP server configuration.
        
        Args:
            server_id: Unique identifier for the server.
            command: Command to start the server.
            args: Command arguments.
            env: Environment variables.
            
        Returns:
            Tuple of (success, message).
        """
        return await self.server_manager.create_custom_server(server_id, command, args, env)
    
    async def get_server_info(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an MCP server.
        
        Args:
            server_id: Identifier of the server.
            
        Returns:
            Server information dictionary, or None if not found.
        """
        return await self.server_manager.get_server_info(server_id)
    
    def list_openrouter_models(self) -> List[Dict[str, Any]]:
        """
        List all available models on OpenRouter.
        
        Returns:
            List of model information dictionaries.
        """
        return self.openrouter_client.list_models()
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        Async wrapper for list_openrouter_models.
        
        Returns:
            List of model information dictionaries.
        """
        return self.list_openrouter_models()
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = "anthropic/claude-3-5-sonnet",
                        tools: Optional[List[Dict[str, Any]]] = None, temperature: float = 0.7,
                        max_tokens: Optional[int] = None, stream: bool = False) -> Union[Dict[str, Any], Any]:
        """
        Generate a chat completion using OpenRouter.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: Model identifier (e.g., 'anthropic/claude-3-5-sonnet').
            tools: Optional list of tool definitions for function calling.
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum tokens to generate.
            stream: Whether to stream the response.
            
        Returns:
            Completion response object.
        """
        return self.openrouter_client.chat_completion(
            messages=messages,
            model=model,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
    
    async def query(self, user_query: str, servers: Optional[List[str]] = None, 
                   model: str = "anthropic/claude-3-5-sonnet", temperature: float = 0.7,
                   max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a query using OpenRouter LLM and available MCP tools.
        
        Args:
            user_query: User query to execute.
            servers: List of MCP server IDs to use. If empty or None, will only use OpenRouter.
            model: OpenRouter model to use.
            temperature: Temperature for the LLM generation.
            max_tokens: Maximum tokens for the LLM response.
            
        Returns:
            Dictionary containing the conversation and other information.
        """
        # Initialize only if we need MCP servers
        if servers and len(servers) > 0:
            await self.initialize(initialize_mcp_client=True)
        else:
            # Skip MCP client initialization if no servers are specified
            await self.initialize(initialize_mcp_client=False)
        
        # Initial conversation
        conversation = {
            "messages": [
                {"role": "user", "content": user_query}
            ],
            "tool_calls": 0
        }
        
        # Start servers if they're not already running
        running_servers = await self.list_running_servers() if servers else {}
        for server_id in servers or []:
            status = running_servers.get(server_id, {})
            if not status.get("running", False):
                logger.info(f"Starting server '{server_id}'...")
                success, error = await self.start_server(server_id)
                if not success:
                    logger.error(f"Failed to start server '{server_id}': {error}")
                    # Continue with other servers
        
        # Get all available tools from the specified servers
        all_tools = []
        for server_id in servers or []:
            try:
                server_tools = await self.get_server_tools(server_id)
                for tool in server_tools:
                    # Add server_id to the tool for tracking
                    tool["server_id"] = server_id
                    all_tools.append(tool)
            except Exception as e:
                logger.error(f"Error getting tools from server '{server_id}': {e}")
                # Continue with other servers
        
        # Start conversation with the model
        conversation_complete = False
        max_turns = 10  # Prevent infinite loops
        turn = 0
        
        while not conversation_complete and turn < max_turns:
            turn += 1
            
            # Get response from the model
            response = self.openrouter_client.chat_completion(
                messages=conversation["messages"],
                model=model,
                tools=all_tools,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract the response message
            assistant_message = response.choices[0].message
            conversation["messages"].append(assistant_message.model_dump())
            
            # Check if the model wants to call a tool
            if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    # Find which server this tool belongs to
                    tool_name = tool_call.function.name
                    server_id = None
                    
                    for tool in all_tools:
                        if tool["name"] == tool_name:
                            server_id = tool.get("server_id")
                            break
                    
                    if not server_id:
                        # Tool not found, inform the model
                        conversation["messages"].append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Error: Tool '{tool_name}' not found in any available server."
                        })
                        continue
                    
                    # Parse arguments
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        conversation["messages"].append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Error: Invalid JSON arguments: {tool_call.function.arguments}"
                        })
                        continue
                    
                    # Call the tool
                    try:
                        result = await self.server_manager.call_tool(server_id, tool_name, args)
                        
                        # Add the result to the conversation
                        conversation["messages"].append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result)
                        })
                    except Exception as e:
                        # If the tool call fails, inform the model
                        conversation["messages"].append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Error calling tool: {str(e)}"
                        })
            else:
                # No tool calls, conversation is complete
                conversation_complete = True
        
        # Return the final conversation
        return {
            "messages": conversation["messages"],
            "response": conversation["messages"][-1]["content"] if conversation["messages"][-1]["role"] == "assistant" else None,
            "tool_calls": conversation["tool_calls"]
        }
    
    async def get_playwright(self) -> PlaywrightMCP:
        """
        Get the Playwright MCP utility.
        
        Returns:
            Initialized PlaywrightMCP instance.
        """
        await self.initialize()
        return self.playwright_mcp
    
    async def close(self) -> None:
        """Close the MCP Router and clean up resources."""
        await self.server_manager.close()


# Command-line interface
async def main():
    """Command-line interface for MCP Router."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Router: Connect Dolphin MCP with OpenRouter")
    parser.add_argument("--config", help="Path to MCP server config file")
    parser.add_argument("--registry", help="Path to MCP server registry file")
    parser.add_argument("--list-servers", action="store_true", help="List available MCP servers")
    parser.add_argument("--list-models", action="store_true", help="List available OpenRouter models")
    parser.add_argument("--install", metavar="SERVER_ID", help="Install an MCP server")
    parser.add_argument("--uninstall", metavar="SERVER_ID", help="Uninstall an MCP server")
    parser.add_argument("--start", metavar="SERVER_ID", help="Start an MCP server")
    parser.add_argument("--stop", metavar="SERVER_ID", help="Stop an MCP server")
    parser.add_argument("--status", metavar="SERVER_ID", help="Get the status of an MCP server")
    parser.add_argument("--query", help="Execute a query using OpenRouter and MCP tools")
    parser.add_argument("--model", default="anthropic/claude-3-5-sonnet", help="Model to use for queries")
    
    args = parser.parse_args()
    
    # Initialize the router
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    if args.list_servers:
        # List available servers
        available_servers = await router.list_available_servers()
        print(f"Available servers ({len(available_servers)}):")
        for server_id, info in available_servers.items():
            print(f"  - {server_id}: {info.get('description', 'No description')}")
        
        # List configured servers
        configured_servers = await router.list_configured_servers()
        print(f"\nConfigured servers ({len(configured_servers)}):")
        for server_id, config in configured_servers.items():
            print(f"  - {server_id}: {config['command']} {' '.join(config.get('args', []))}")
        
        # List running servers
        running_servers = await router.list_running_servers()
        print(f"\nRunning servers ({len(running_servers)}):")
        for server_id, status in running_servers.items():
            running = "RUNNING" if status["running"] else "STOPPED"
            pid = status["pid"] or "N/A"
            uptime = f"{status['uptime']:.2f}s" if status["uptime"] else "N/A"
            print(f"  - {server_id}: {running} (PID: {pid}, Uptime: {uptime})")
    
    elif args.list_models:
        # List available OpenRouter models
        models = await router.list_models()
        print(f"Available OpenRouter models ({len(models)}):")
        for model in models:
            print(f"  - {model.get('id')}: {model.get('context_length')} context length")
    
    elif args.install:
        # Install a server
        server_id = args.install
        success, output, config = await router.install_server(server_id)
        if success:
            print(f"Successfully installed server '{server_id}'")
        else:
            print(f"Failed to install server '{server_id}': {output}")
    
    elif args.uninstall:
        # Uninstall a server
        server_id = args.uninstall
        success, output = await router.uninstall_server(server_id)
        if success:
            print(f"Successfully uninstalled server '{server_id}'")
        else:
            print(f"Failed to uninstall server '{server_id}': {output}")
    
    elif args.start:
        # Start a server
        server_id = args.start
        success, error = await router.start_server(server_id)
        if success:
            print(f"Successfully started server '{server_id}'")
        else:
            print(f"Failed to start server '{server_id}': {error}")
    
    elif args.stop:
        # Stop a server
        server_id = args.stop
        success, error = await router.stop_server(server_id)
        if success:
            print(f"Successfully stopped server '{server_id}'")
        else:
            print(f"Failed to stop server '{server_id}': {error}")
    
    elif args.status:
        # Get server status
        server_id = args.status
        status = await router.get_server_status(server_id)
        running = "RUNNING" if status["running"] else "STOPPED"
        pid = status["pid"] or "N/A"
        uptime = f"{status['uptime']:.2f}s" if status["uptime"] else "N/A"
        memory = f"{status['memory_usage']:.2f} MB" if status["memory_usage"] else "N/A"
        print(f"Status of server '{server_id}':")
        print(f"  Status: {running}")
        print(f"  PID: {pid}")
        print(f"  Uptime: {uptime}")
        print(f"  Memory usage: {memory}")
        
        if status["running"]:
            tools = await router.get_server_tools(server_id)
            print(f"  Tools: {len(tools)}")
            for tool in tools:
                print(f"    - {tool['name']}: {tool.get('description', 'No description')}")
    
    elif args.query:
        # Execute a query
        result = await router.query(args.query, model=args.model)
        
        # Print the conversation
        for message in result["messages"]:
            role = message["role"]
            if role == "user":
                print(f"\nUser: {message['content']}")
            elif role == "assistant":
                print(f"\nAssistant: {message['content']}")
            elif role == "tool":
                print(f"\nTool result: {message['content']}")
        
        print(f"\nQuery completed with {result['tool_calls']} tool calls.")
    
    # Close the router
    await router.close()


if __name__ == "__main__":
    asyncio.run(main())
