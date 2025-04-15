import google.generativeai as genai
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from src.core import MCPLogger, MCPTools
from src.llm.base import BaseLLMAdapter

class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, 
                 model_name: str = 'gemini-1.5-flash',
                 debug: bool = False,
                 log_file: Optional[Path] = None):
        super().__init__(model_name, debug, log_file)

    async def configure(self, api_key: str, **kwargs) -> None:
        self.logger.log_debug(f"Configuring Gemini with model {self.model_name}")
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                tools=self.tools
            )
            self.chat = self.model.start_chat()
            self.logger.log_info("Successfully configured Gemini model")
        except Exception as e:
            self.logger.log_error(f"Failed to configure Gemini: {str(e)}")
            raise

    async def prepare_tools(self, mcp_tools: MCPTools) -> Dict:
        """Prepare tools for Gemini model"""
        tools = mcp_tools.list_tools()
        self.logger.log_debug(f"Preparing {len(tools)} tools for Gemini")
        self.tools = [{"function_declarations": []}]
        try:
            for tool in tools:
                self.logger.log_debug(f"Converting tool: {tool.name}")

                # Clean up properties to remove 'default' field
                properties = {}
                for key, value in tool.properties.items():
                    if isinstance(value, dict) and 'default' in value:
                        cleaned_value = value.copy()
                        del cleaned_value['default']
                        properties[key] = cleaned_value
                    else:
                        properties[key] = value

                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": tool.function_type,
                        "properties": properties,
                        "required": tool.required
                    },
                }
                self.tools[0]["function_declarations"].append(tool_dict)
            
            self.logger.log_info(f"Successfully prepared {len(tools)} tools")
            return self.tools
            
        except Exception as e:
            self.logger.log_error(f"Failed to prepare tools: {str(e)}")
            raise

    async def send_message(self, message: str) -> Any:
        self.logger.log_debug(f"Sending message to Gemini: {message[:100]}...")
        try:
            response = await self.chat.send_message_async(message)
            self.logger.log_info("Successfully received response from Gemini")
            return response
        except Exception as e:
            self.logger.log_error(f"Failed to send message: {str(e)}")
            raise

    def extract_tool_call(self, response: Any) -> tuple[str, Dict[str, Any]]:
        """
        Extract tool call using the tool's schema definition.
        """
        try:
            function_call = response.parts[0].function_call
            tool_name = str(function_call.name)
            
            # Get the tool schema
            tool = next((t for t in self.tools[0]["function_declarations"] 
                        if t["name"] == tool_name), None)
            
            if not tool:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            # Extract according to schema
            raw_args = function_call.args
            tool_args = self._extract_by_schema(raw_args, tool["parameters"])
            
            self.logger.log_debug(f"Extracted arguments: {tool_args}")
            return tool_name, tool_args
            
        except Exception as e:
            self.logger.log_error(f"Failed to extract tool call: {str(e)}")
            raise