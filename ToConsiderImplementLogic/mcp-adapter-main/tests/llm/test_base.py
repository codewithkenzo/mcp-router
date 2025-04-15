"""
Tests for the base LLM adapter.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock
from src.llm.base import BaseLLMAdapter

class ConcreteLLMAdapter(BaseLLMAdapter):
    """Concrete implementation of BaseLLMAdapter for testing."""
    
    async def configure(self, api_key, **kwargs):
        """Implement abstract method."""
        self.api_key = api_key
        self.configured = True
        
    async def prepare_tools(self, mcp_tools):
        """Implement abstract method."""
        self.prepared_tools = mcp_tools
        return {"tools": mcp_tools}
        
    async def send_message(self, message):
        """Implement abstract method."""
        self.last_message = message
        return f"Response to: {message}"
        
    def extract_tool_call(self, response):
        """Implement abstract method."""
        # Simple implementation that assumes response is in format "tool_name|param1=value1,param2=value2"
        if isinstance(response, str) and "|" in response:
            tool_part, args_part = response.split("|")
            tool_name = tool_part.strip()
            
            args = {}
            if args_part:
                for arg in args_part.split(","):
                    if "=" in arg:
                        key, value = arg.split("=")
                        args[key.strip()] = value.strip()
            
            return tool_name, args
        return None, None

class TestBaseLLMAdapter(unittest.TestCase):
    """Test the BaseLLMAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adapter = ConcreteLLMAdapter(
            model_name="test-model",
            debug=True,
            log_file=Path("/tmp/test_adapter.log")
        )
        
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.model_name, "test-model")
        self.assertIsNone(self.adapter.model)
        self.assertIsNone(self.adapter.chat)
        self.assertIsNone(self.adapter.tools)
        
    def test_extract_by_schema_string(self):
        """Test extracting string values."""
        schema = {"type": "string"}
        value = "test"
        result = self.adapter._extract_by_schema(value, schema)
        self.assertEqual(result, "test")
        
        # Test conversion
        result = self.adapter._extract_by_schema(123, schema)
        self.assertEqual(result, "123")
        
    def test_extract_by_schema_number(self):
        """Test extracting number values."""
        schema = {"type": "number"}
        value = 123.45
        result = self.adapter._extract_by_schema(value, schema)
        self.assertEqual(result, 123.45)
        
        # Test conversion
        result = self.adapter._extract_by_schema("123.45", schema)
        self.assertEqual(result, 123.45)
        
    def test_extract_by_schema_integer(self):
        """Test extracting integer values."""
        schema = {"type": "integer"}
        value = 123
        result = self.adapter._extract_by_schema(value, schema)
        self.assertEqual(result, 123)
        
        # Test conversion
        result = self.adapter._extract_by_schema("123", schema)
        self.assertEqual(result, 123)
        
    def test_extract_by_schema_boolean(self):
        """Test extracting boolean values."""
        schema = {"type": "boolean"}
        value = True
        result = self.adapter._extract_by_schema(value, schema)
        self.assertTrue(result)
        
        # Test conversion
        result = self.adapter._extract_by_schema("true", schema)
        self.assertTrue(result)
        
    def test_extract_by_schema_array(self):
        """Test extracting array values."""
        schema = {
            "type": "array",
            "items": {"type": "string"}
        }
        value = ["apple", "banana", "cherry"]
        result = self.adapter._extract_by_schema(value, schema)
        self.assertEqual(result, ["apple", "banana", "cherry"])
        
        # Test items conversion
        schema = {
            "type": "array",
            "items": {"type": "integer"}
        }
        value = ["1", "2", "3"]
        result = self.adapter._extract_by_schema(value, schema)
        self.assertEqual(result, [1, 2, 3])
        
        # Test non-iterable
        result = self.adapter._extract_by_schema(123, schema)
        self.assertEqual(result, [])
        
    def test_extract_by_schema_object(self):
        """Test extracting object values."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        value = {"name": "Alice", "age": "30", "extra": "ignored"}
        result = self.adapter._extract_by_schema(value, schema)
        self.assertEqual(result, {"name": "Alice", "age": 30})
        
        # Test non-dict
        result = self.adapter._extract_by_schema("not an object", schema)
        self.assertEqual(result, {})
        
    def test_extract_by_schema_default(self):
        """Test extracting values with unknown schema type."""
        schema = {"type": "unknown"}
        value = "test"
        result = self.adapter._extract_by_schema(value, schema)
        self.assertEqual(result, "test")
        
if __name__ == "__main__":
    unittest.main()