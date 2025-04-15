from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from openai import OpenAI
import json

from src.llm.base import BaseLLMAdapter
from src.core.tools import MCPTools
from src.core.logger import MCPLogger

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, 
                 model_name: str = 'gpt-4o-mini',
                 debug: bool = False,
                 log_file: Optional[Path] = None):
        super().__init__(model_name, debug, log_file)
        
    async def configure(self, api_key: str, **kwargs):
        """Configure OpenAI client with API key"""
        try:
            self.client = OpenAI(api_key=api_key)
            self.logger.log_info(f"Successfully configured OpenAI client with model {self.model_name}")
        except Exception as e:
            self.logger.log_error(f"Failed to configure OpenAI client: {str(e)}")
            raise e

    async def prepare_tools(self, mcp_tools: MCPTools) -> Dict:
        """Prepare tools for OpenAI model"""
        tools = mcp_tools.list_tools()
        self.logger.log_debug(f"Preparing {len(tools)} tools for OpenAI")
        self.tools = []
        
        try:
            for tool in tools:
                self.logger.log_debug(f"Converting tool: {tool.name}")
                
                tool_dict = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": tool.function_type,
                            "properties": tool.properties,
                            "required": tool.required
                        }
                    }
                }
                self.tools.append(tool_dict)
            
            self.logger.log_info(f"Successfully prepared {len(tools)} tools")
            return self.tools
            
        except Exception as e:
            self.logger.log_error(f"Failed to prepare tools: {str(e)}")
            raise e

    async def send_message(self, message: str) -> Any:
        """Send a message to OpenAI and get response"""
        self.logger.log_debug(f"Sending message to OpenAI: {message[:100]}...")
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": message}],
                tools=self.tools
            )
            self.logger.log_info("Successfully received response from OpenAI")
            return completion
            
        except Exception as e:
            self.logger.log_error(f"Failed to send message: {str(e)}")
            raise e

    def extract_tool_call(self, response: Any) -> Tuple[str, Dict[str, Any]]:
        """Extract tool call using the tool's schema definition"""
        try:
            if not response.choices[0].message.tool_calls:
                return None, None
                
            tool_call = response.choices[0].message.tool_calls[0]
            tool_name = tool_call.function.name
            
            # Find the tool schema
            tool_schema = None
            for tool in self.tools:
                if tool["function"]["name"] == tool_name:
                    tool_schema = tool["function"]["parameters"]
                    break
            
            if not tool_schema:
                self.logger.log_error(f"Schema not found for tool: {tool_name}")
                return None, None
            
            # Extract arguments according to schema
            args_dict = json.loads(tool_call.function.arguments)
            tool_args = self._extract_by_schema(args_dict, tool_schema)
            
            self.logger.log_debug(f"Extracted arguments: {tool_args}")
            return tool_name, tool_args
            
        except Exception as e:
            self.logger.log_error(f"Failed to extract tool call: {str(e)}")
            return None, None
