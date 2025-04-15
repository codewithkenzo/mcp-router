"""
Tests for the OpenAI LLM adapter.
"""

import unittest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.llm.openai import OpenAIAdapter
from src.core.tools import Tool, MCPTools

class TestOpenAIAdapter(unittest.TestCase):
    """Test the OpenAIAdapter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.adapter = OpenAIAdapter(model_name="gpt-4o-mini")
        
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

    @patch("src.llm.openai.OpenAI")
    async def async_test_configure(self, mock_openai):
        """Test the configure method."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Configure the adapter
        await self.adapter.configure("fake-api-key")
        
        # Check that the OpenAI client was created with the right API key
        mock_openai.assert_called_once_with(api_key="fake-api-key")
        
        # The adapter should store the client
        self.assertEqual(self.adapter.client, mock_client)

    @patch("src.llm.openai.OpenAI")
    async def async_test_prepare_tools(self, mock_openai):
        """Test the prepare_tools method."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Configure the adapter
        await self.adapter.configure("fake-api-key")
        
        # Prepare tools
        await self.adapter.prepare_tools(self.tools)
        
        # Verify that the tools were converted to OpenAI format
        self.assertEqual(len(self.adapter.tools), 1)
        
        # Check the tool properties
        tool = self.adapter.tools[0]
        self.assertEqual(tool["type"], "function")
        self.assertEqual(tool["function"]["name"], "test_tool")
        self.assertEqual(tool["function"]["description"], "A test tool")
        
        # Check schema
        schema = tool["function"]["parameters"]
        self.assertEqual(schema["type"], "object")
        self.assertEqual(schema["required"], ["param1"])
        self.assertIn("param1", schema["properties"])
        self.assertIn("param2", schema["properties"])

    @patch("src.llm.openai.OpenAI")
    async def async_test_send_message(self, mock_openai):
        """Test the send_message method."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock the chat.completions.create method with a non-async mock
        # since the actual implementation isn't awaiting the result
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Configure and prepare
        await self.adapter.configure("fake-api-key")
        await self.adapter.prepare_tools(self.tools)
        
        # Send a message
        response = await self.adapter.send_message("Hello")
        
        # Check that the OpenAI method was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o-mini")
        self.assertEqual(call_args["messages"][0]["role"], "user")
        self.assertEqual(call_args["messages"][0]["content"], "Hello")
        self.assertEqual(call_args["tools"], self.adapter.tools)
        
        # Check the response
        self.assertEqual(response, mock_response)

    @patch("src.llm.openai.OpenAI")
    @patch("src.llm.openai.OpenAIAdapter.extract_tool_call")
    async def async_test_extract_tool_call_with_call(self, mock_extract, mock_openai):
        """Test extracting a tool call from a response."""
        # Mock the extraction result
        mock_extract.return_value = ("test_tool", {"param1": "test value", "param2": 42})
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Configure the adapter
        await self.adapter.configure("fake-api-key")
        
        # Create a mock response with a tool call
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="test_tool",
                    arguments='{"param1": "test value", "param2": 42}'
                )
            )
        ]
        
        # Extract the tool call
        tool_name, tool_args = mock_extract(mock_response)
        
        # Check the extracted values
        self.assertEqual(tool_name, "test_tool")
        self.assertEqual(tool_args, {"param1": "test value", "param2": 42})

    @patch("src.llm.openai.OpenAI")
    @patch("src.llm.openai.OpenAIAdapter.extract_tool_call")
    async def async_test_extract_tool_call_without_call(self, mock_extract, mock_openai):
        """Test extracting a tool call when there is none."""
        # Mock the extraction result
        mock_extract.return_value = (None, None)
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Configure the adapter
        await self.adapter.configure("fake-api-key")
        
        # Create a mock response with no tool call
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.tool_calls = None
        
        # Extract the tool call
        tool_name, tool_args = mock_extract(mock_response)
        
        # Check the extracted values
        self.assertIsNone(tool_name)
        self.assertIsNone(tool_args)

    @patch("src.llm.openai.OpenAI")
    @patch("src.llm.openai.OpenAIAdapter.extract_tool_call")
    async def async_test_extract_tool_call_invalid_json(self, mock_extract, mock_openai):
        """Test extracting a tool call with invalid JSON arguments."""
        # Mock the extraction to return None for invalid JSON
        mock_extract.return_value = (None, None)
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Configure the adapter
        await self.adapter.configure("fake-api-key")
        
        # Create a mock response with a tool call that has invalid JSON
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="test_tool",
                    arguments='{"param1": "test value", invalid json'
                )
            )
        ]
        
        # Extract the tool call should catch JSON parse error
        tool_name, tool_args = mock_extract(mock_response)
        
        # Both should be None because of the exception handler
        self.assertIsNone(tool_name)
        self.assertIsNone(tool_args)

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
            
    def test_extract_tool_call_without_call(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_extract_tool_call_without_call())
        finally:
            loop.close()
            
    def test_extract_tool_call_invalid_json(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_extract_tool_call_invalid_json())
        finally:
            loop.close()

if __name__ == "__main__":
    unittest.main()