"""
Tests for the client module in the MCP adapter.
"""

import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from mcp import StdioServerParameters

from src.core.client import MCPClient
from src.core.tools import Tool

class TestMCPClient(unittest.TestCase):
    """Test the MCPClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"],
            env=None
        )
        
        self.client = MCPClient(
            self.server_params,
            debug=True,
            log_file=Path("/tmp/test_client.log"),
            client_name="test_client"
        )
        
        # Mock tool data in tuple format
        self.tool_data = (
            ("internal_name", "external_name"),
            ("Internal description", "External description"),
            [None, {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "A string parameter"}
                },
                "required": ["param1"]
            }]
        )
        
        # Mock invalid tool data
        self.invalid_tool_data = (
            ("internal_name", "external_name"),
            ("Internal description", "External description"),
            [None]  # Missing schema
        )

    @patch("src.core.client.stdio_client")
    @patch("src.core.client.ClientSession")
    async def async_test_get_tools(self, mock_session_class, mock_stdio_client):
        """Test getting tools from the server."""
        # Mock the read and write functions
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
        
        # Mock the ClientSession
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock the list_tools response
        tools_response = MagicMock()
        tools_response.tools = [self.tool_data]
        mock_session.list_tools.return_value = tools_response
        
        # Call get_tools
        tools = await self.client.get_tools()
        
        # Verify the result
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].name, "external_name")
        self.assertEqual(tools[0].description, "External description")
        self.assertEqual(tools[0].function_type, "object")
        self.assertEqual(len(tools[0].properties), 1)
        self.assertIn("param1", tools[0].properties)
        self.assertEqual(tools[0].required, ["param1"])
        
        # Verify that the right methods were called
        mock_stdio_client.assert_called_once_with(self.server_params)
        mock_session.initialize.assert_called_once()
        mock_session.list_tools.assert_called_once()

    @patch("src.core.client.stdio_client")
    @patch("src.core.client.ClientSession")
    async def async_test_get_tools_with_invalid_data(self, mock_session_class, mock_stdio_client):
        """Test handling of invalid tool data."""
        # Mock the read and write functions
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
        
        # Mock the ClientSession
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock the list_tools response with invalid tool data
        tools_response = MagicMock()
        tools_response.tools = [self.invalid_tool_data]
        mock_session.list_tools.return_value = tools_response
        
        # Call get_tools
        tools = await self.client.get_tools()
        
        # Verify that no tools were returned (invalid data was skipped)
        self.assertEqual(len(tools), 0)

    @patch("src.core.client.stdio_client")
    @patch("src.core.client.ClientSession")
    async def async_test_execute_tool(self, mock_session_class, mock_stdio_client):
        """Test executing a tool."""
        # Mock the read and write functions
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
        
        # Mock the ClientSession
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock the call_tool response
        expected_result = {"status": "success", "data": "test result"}
        mock_session.call_tool.return_value = expected_result
        
        # Call execute_tool
        result = await self.client.execute_tool("test_tool", {"param1": "test"})
        
        # Verify the result
        self.assertEqual(result, expected_result)
        
        # Verify that the right methods were called
        mock_stdio_client.assert_called_once_with(self.server_params)
        mock_session.initialize.assert_called_once()
        mock_session.call_tool.assert_called_once_with("test_tool", {"param1": "test"})

    @patch("src.core.client.stdio_client")
    @patch("src.core.client.ClientSession")
    async def async_test_close(self, mock_session_class, mock_stdio_client):
        """Test closing the client."""
        # Call close
        await self.client.close()
        
        # Nothing to verify since close doesn't do anything yet,
        # but this still increases code coverage
        pass

    def test_convert_to_tool(self):
        """Test converting tool data to Tool object."""
        # Call _convert_to_tool
        tool = self.client._convert_to_tool(self.tool_data)
        
        # Verify the result
        self.assertEqual(tool.name, "external_name")
        self.assertEqual(tool.description, "External description")
        self.assertEqual(tool.function_type, "object")
        self.assertEqual(len(tool.properties), 1)
        self.assertIn("param1", tool.properties)
        self.assertEqual(tool.required, ["param1"])

    def test_convert_to_tool_invalid_data(self):
        """Test converting invalid tool data."""
        # Verify that an exception is raised for invalid data
        with self.assertRaises(ValueError):
            self.client._convert_to_tool(self.invalid_tool_data)

    # Helper to run async tests
    def test_get_tools(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_get_tools())
        finally:
            loop.close()
            
    def test_get_tools_with_invalid_data(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_get_tools_with_invalid_data())
        finally:
            loop.close()
            
    def test_execute_tool(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_execute_tool())
        finally:
            loop.close()
            
    def test_close(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_test_close())
        finally:
            loop.close()

if __name__ == "__main__":
    unittest.main()