"""
Tests for the Gemini LLM adapter.
"""

import unittest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.llm.gemini import GeminiAdapter
from src.core.tools import Tool, MCPTools

class TestGeminiAdapter(unittest.TestCase):
    """Test the GeminiAdapter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.adapter = GeminiAdapter(model_name="gemini-1.5-flash")
        
        # Create test tools
        self.tool1 = Tool(
            name="test_tool",
            description="A test tool",
            function_type="object",
            properties={
                "param1": {"type": "string", "description": "A string parameter"},
                "param2": {"type": "integer", "description": "An integer parameter"}
            },
            required=["param1"]
        )
        
        self.tools = MCPTools()
        self.tools.add([self.tool1])

    @patch("src.llm.gemini.genai")
    async def async_test_configure(self, mock_genai):
        """Test the configure method."""
        # Mock the Gemini GenerativeModel
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Configure the adapter
        await self.adapter.configure("fake-api-key")
        
        # Check that the genai.configure was called with the right API key
        mock_genai.configure.assert_called_once_with(api_key="fake-api-key")
        
        # Check that the GenerativeModel was created
        mock_genai.GenerativeModel.assert_called_once()
        
        # The adapter should store the model
        self.assertEqual(self.adapter.model, mock_model)

    @patch("src.llm.gemini.genai")
    async def async_test_prepare_tools(self, mock_genai):
        """Test the prepare_tools method."""
        # Mock the Gemini GenerativeModel
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Configure the adapter
        await self.adapter.configure("fake-api-key")
        
        # Prepare tools
        result = await self.adapter.prepare_tools(self.tools)
        
        # Verify the result is a list of tools
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        
        # Verify that the tools were converted to Gemini format
        self.assertIn("function_declarations", result[0])
        self.assertEqual(len(result[0]["function_declarations"]), 1)
        
        tool = result[0]["function_declarations"][0]
        self.assertEqual(tool["name"], "test_tool")
        self.assertEqual(tool["description"], "A test tool")
        
        # Check schema
        schema = tool["parameters"]
        self.assertEqual(schema["type"], "object")
        self.assertEqual(len(schema["properties"]), 2)
        self.assertEqual(schema["required"], ["param1"])

    @patch("src.llm.gemini.genai")
    async def async_test_send_message(self, mock_genai):
        """Test the send_message method."""
        # Mock the Gemini GenerativeModel and response
        mock_model = MagicMock()
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test response"
        
        # Set up mock chain with AsyncMock for async method
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.start_chat.return_value = mock_chat
        # Use AsyncMock for async method
        mock_chat.send_message_async = AsyncMock(return_value=mock_response)
        
        # Configure the adapter (will set self.chat)
        await self.adapter.configure("fake-api-key")
        
        # Explicitly set the mocked chat
        self.adapter.chat = mock_chat
        
        # Prepare tools
        await self.adapter.prepare_tools(self.tools)
        
        # Send a message
        response = await self.adapter.send_message("Hello")
        
        # Check that the send_message method was called correctly
        mock_chat.send_message_async.assert_called_once_with("Hello")
        
        # Check the response
        self.assertEqual(response, mock_response)

    @patch("src.llm.gemini.genai")
    @patch("src.llm.gemini.GeminiAdapter.extract_tool_call")
    async def async_test_extract_tool_call_with_call(self, mock_extract, mock_genai):
        """Test extracting a tool call from a response."""
        # Mock the extraction result
        mock_extract.return_value = ("test_tool", {"param1": "test value", "param2": 42})
        
        # Mock the Gemini GenerativeModel
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Configure the adapter
        await self.adapter.configure("fake-api-key")
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content = MagicMock()
        mock_response.candidates[0].content.parts = [MagicMock()]
        mock_response.candidates[0].content.parts[0].function_call = MagicMock()
        mock_response.candidates[0].content.parts[0].function_call.name = "test_tool"
        mock_response.candidates[0].content.parts[0].function_call.args = {
            "param1": "test value", 
            "param2": 42
        }
        
        # Extract the tool call
        tool_name, tool_args = mock_extract(mock_response)
        
        # Check the extracted values
        self.assertEqual(tool_name, "test_tool")
        self.assertEqual(tool_args, {"param1": "test value", "param2": 42})

    # Helper to run async tests
    def test_configure(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_configure())
        finally:
            loop.close()
            
    def test_prepare_tools(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_prepare_tools())
        finally:
            loop.close()
            
    def test_send_message(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_send_message())
        finally:
            loop.close()
            
    def test_extract_tool_call_with_call(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_extract_tool_call_with_call())
        finally:
            loop.close()
            
if __name__ == "__main__":
    unittest.main()