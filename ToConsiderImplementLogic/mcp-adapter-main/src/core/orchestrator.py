from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
from pathlib import Path

from src.core.logger import MCPLogger
from src.core.client import MCPClient
from src.core.tools import Tool, MCPTools
from mcp import StdioServerParameters

@dataclass
class ToolResult:
    """Represents the result of a tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    client_name: Optional[str] = None

class ToolOrchestrator:
    """Orchestrates MCP servers, clients and tool execution"""
    def __init__(self, 
                 server_params: List[StdioServerParameters],
                 debug: bool = False,
                 log_dir: Optional[Path] = None):
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = MCPLogger(
            "orchestrator",
            debug_mode=debug,
            log_file=self.log_dir / "orchestrator.log"
        )
        self.clients: Dict[str, MCPClient] = {}
        self.tools = MCPTools()
        self.tool_to_client: Dict[str, str] = {}
        self._initialize_clients(server_params, debug)

    def _get_client_name(self, params: StdioServerParameters) -> str:
        package = params.args[1].split('/')[-1]
        return package.replace('server-', '')

    def _initialize_clients(self, 
                          server_params: List[StdioServerParameters],
                          debug: bool):
        """Initialize MCP clients for each server"""
        for params in server_params:
            client_name = self._get_client_name(params)
            client = MCPClient(
                params,
                debug=debug,
                log_file=self.log_dir / f"{client_name}.log",
                client_name=client_name
            )
            self.clients[client_name] = client

    async def initialize(self):
        """Initialize tools from all clients"""
        for client_name, client in self.clients.items():
            try:
                # Get tools from each client
                tools = await client.get_tools()
                self.logger.log_debug(f"Retrieved tools from {client_name}:")
                for tool in tools:
                    self.logger.log_debug(f"Tool structure: {tool}")
                    
                    # Map tool to client
                    if isinstance(tool, Tool):
                        tool_name = tool.name
                        self.tool_to_client[tool_name] = client_name
                        self.logger.log_debug(f"  - {tool_name}")
                    else:
                        # Handle tuple structure
                        try:
                            (internal_name, external_name), _, _ = tool
                            tool_name = external_name
                            self.tool_to_client[tool_name] = client_name
                            self.logger.log_debug(f"  - {tool_name}")
                        except Exception as e:
                            self.logger.log_error(f"Error parsing tool tuple: {str(e)}")
                            continue
                
                # Add tools to collection
                self.tools.add(tools)
                self.logger.log_info(f"Initialized {len(tools)} tools from client: {client_name}")
            except Exception as e:
                self.logger.log_error(f"Error initializing tools from client {client_name}: {str(e)}")
                self.logger.log_error(f"Exception details: {str(e.__class__.__name__)}")
                import traceback
                self.logger.log_error(f"Traceback: {traceback.format_exc()}")

    async def execute(self, tool_name: str, args: Dict[str, Any]) -> ToolResult:
        """Execute a tool using the appropriate client"""
        # Find the client for this tool
        client_name = self.tool_to_client.get(tool_name)
        if not client_name:
            return ToolResult(
                success=False,
                data=None,
                error=f"No client found for tool '{tool_name}'",
                client_name=None
            )

        client = self.clients[client_name]
        
        # Get tool schema for validation
        tool = self.tools.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool '{tool_name}' not found",
                client_name=client_name
            )

        # Validate arguments
        missing_args = [arg for arg in tool.required if arg not in args]
        if missing_args:
            return ToolResult(
                success=False,
                data=None,
                error=f"Missing required arguments: {', '.join(missing_args)}",
                client_name=client_name
            )

        try:
            # Execute tool
            self.logger.log_info(f"Executing tool '{tool_name}' using client '{client_name}'")
            result = await client.execute_tool(tool_name, args)
            return ToolResult(
                success=True,
                data=result,
                client_name=client_name
            )
        except Exception as e:
            self.logger.log_error(f"Error executing tool {tool_name} with client {client_name}: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                client_name=client_name
            )

    async def close(self):
        """Close all clients"""
        for client in self.clients.values():
            await client.close()
