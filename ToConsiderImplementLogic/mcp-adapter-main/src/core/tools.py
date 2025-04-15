from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

from src.core.logger import MCPLogger

class Tool:
    def __init__(self, name: str, 
                 description: str, 
                 function_type: str, 
                 properties: Dict[str, Any],
                 required: List[str]):
        self.name = name
        self.description = description
        self.function_type = function_type
        self.properties = properties
        self.required = required


class MCPTools:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.logger = MCPLogger("tools")
    
    def add(self, tools: List[Union[Tool, Tuple[Tuple[str, str], Tuple[str, str], List[Dict[str, Any]]]]]) -> None:
        """Add tools to the collection
        
        Args:
            tools: List of either:
                - Tool objects directly from server
                - Tool tuples containing:
                    - name tuple (internal_name, external_name)
                    - description tuple (internal_desc, external_desc)
                    - list containing [None, schema_dict]
        """
        for tool in tools:
            try:
                if isinstance(tool, Tool):
                    # Tool object already properly formatted
                    self.tools[tool.name] = tool
                    self.logger.log_debug(f"Added tool object: {tool.name}")
                else:
                    # Parse tuple structure
                    (internal_name, external_name), (internal_desc, external_desc), schema_list = tool
                    
                    if not schema_list or len(schema_list) < 2 or not isinstance(schema_list[1], dict):
                        self.logger.log_warning(f"Invalid schema for tool {external_name}: {schema_list}")
                        continue
                    
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
                    
                    new_tool = Tool(
                        name=external_name,
                        description=external_desc,
                        function_type=function_type,
                        properties=properties,
                        required=required
                    )
                    self.tools[external_name] = new_tool
                    self.logger.log_debug(f"Added tool tuple: {external_name}")
            except Exception as e:
                tool_name = tool.name if isinstance(tool, Tool) else "unknown"
                self.logger.log_error(f"Error adding tool {tool_name}: {str(e)}")
                import traceback
                self.logger.log_error(f"Traceback: {traceback.format_exc()}")
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        return self.tools.get(tool_name)
        
    def get_desc(self, tool_name: str) -> Optional[str]:
        tool = self.get_tool(tool_name)
        return tool.description if tool else None
        
    def list_tools(self) -> List[Tool]:
        return list(self.tools.values())
        
    def remove_tool(self, tool_name: str):
        self.tools.pop(tool_name, None)
