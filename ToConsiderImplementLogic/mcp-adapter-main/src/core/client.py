from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from src.core.logger import MCPLogger
from src.core.tools import Tool

class MCPClient:
    def __init__(self, 
                 server_params: StdioServerParameters, 
                 debug: bool = False,
                 log_file: Optional[Path] = None,
                 client_name: Optional[str] = "MCPClient"):
        self.server_params = server_params
        self.logger = MCPLogger(client_name, debug_mode=debug, log_file=log_file)
        self._current_session = None

    def _convert_to_tool(self, tool_data: Tuple[Tuple[str, str], Tuple[str, str], List[Dict[str, Any]]]) -> Tool:
        """Convert raw tool data from server to Tool object"""
        try:
            (internal_name, external_name), (internal_desc, external_desc), schema_list = tool_data
            
            if not schema_list or len(schema_list) < 2 or not isinstance(schema_list[1], dict):
                raise ValueError(f"Invalid schema for tool {external_name}: {schema_list}")
            
            schema = schema_list[1]
            function_type = schema.get("type", "object")
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            if not properties:
                properties = {
                    "_dummy": {
                        "type": "string",
                        "description": "Unused parameter"
                    }
                }
            
            return Tool(
                name=external_name,
                description=external_desc,
                function_type=function_type,
                properties=properties,
                required=required
            )
        except Exception as e:
            self.logger.log_error(f"Error converting tool data: {str(e)}")
            raise

    async def get_tools(self) -> List[Tool]:
        self.logger.log_debug("Retrieving tools from MCP server")
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.logger.log_debug("Initializing session")
                    await session.initialize()
                    tools = await session.list_tools()
                    
                    # Convert raw tool data to Tool objects
                    tool_objects = []
                    for tool_data in tools.tools:
                        try:
                            tool = self._convert_to_tool(tool_data)
                            tool_objects.append(tool)
                        except Exception as e:
                            self.logger.log_error(f"Skipping tool due to conversion error: {str(e)}")
                            continue
                    
                    self.logger.log_info(f"Retrieved {len(tool_objects)} tools")
                    return tool_objects
        except Exception as e:
            self.logger.log_error(f"Failed to get tools: {str(e)}")
            raise

    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        self.logger.log_debug(f"Executing tool {tool_name} with args: {tool_args}")
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.logger.log_debug("Initializing session")
                    await session.initialize()
                    result = await session.call_tool(tool_name, tool_args)
                    self.logger.log_info(f"Successfully executed tool {tool_name}")
                    return result
        except Exception as e:
            self.logger.log_error(f"Failed to execute tool {tool_name}: {str(e)}")
            raise

    async def close(self):
        """Clean up any resources"""
        self.logger.log_debug("Closing client")
        # Nothing to clean up for now, but this method exists for future use
        # and interface consistency