from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from src.core import MCPLogger, MCPTools

class BaseLLMAdapter(ABC):
    """Base class for LLM adapters"""
    
    def __init__(self, 
                 model_name: str,
                 debug: bool = False,
                 log_file: Optional[Path] = None):
        self.model_name = model_name
        self.model = None
        self.chat = None
        self.tools = None
        self.logger = MCPLogger(self.__class__.__name__, debug_mode=debug, log_file=log_file)

    @abstractmethod
    async def configure(self, api_key: str, **kwargs) -> None:
        """Configure the LLM with API key and other settings"""
        pass

    @abstractmethod
    async def prepare_tools(self, mcp_tools: List[Any]) -> Dict:
        """Prepare tools for the LLM"""
        pass

    @abstractmethod
    async def send_message(self, message: str) -> Any:
        """Send a message to the LLM and get response"""
        pass

    @abstractmethod
    def extract_tool_call(self, response: Any) -> Tuple[str, Dict[str, Any]]:
        """Extract tool call from LLM response"""
        pass

    def _extract_by_schema(self, value: Any, schema: Dict[str, Any]) -> Any:
        """Extract value according to the schema definition"""
        # Handle primitive types
        if schema.get("type") == "string":
            return str(value)
        elif schema.get("type") == "number":
            return float(value)
        elif schema.get("type") == "integer":
            return int(value)
        elif schema.get("type") == "boolean":
            return bool(value)
            
        # Handle arrays
        elif schema.get("type") == "array":
            items_schema = schema.get("items", {})
            if hasattr(value, '__iter__'):
                return [self._extract_by_schema(item, items_schema) for item in value]
            return []
            
        # Handle objects
        elif schema.get("type") == "object":
            if hasattr(value, 'items'):
                properties = schema.get("properties", {})
                result = {}
                items = dict(value.items())
                
                for prop_name, prop_schema in properties.items():
                    if prop_name in items:
                        result[prop_name] = self._extract_by_schema(items[prop_name], prop_schema)
                        
                return result
            return {}
            
        # Default
        return value
