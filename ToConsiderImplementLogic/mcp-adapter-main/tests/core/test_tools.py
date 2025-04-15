"""
Tests for the tools module in the MCP adapter.
"""

import unittest
from src.core.tools import Tool, MCPTools

class TestTool(unittest.TestCase):
    """Test the Tool class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = Tool(
            name="test_tool",
            description="A test tool for testing",
            function_type="object",
            properties={
                "param1": {"type": "string", "description": "A string parameter"},
                "param2": {"type": "integer", "description": "An integer parameter"}
            },
            required=["param1"]
        )

    def test_tool_init(self):
        """Test Tool initialization."""
        self.assertEqual(self.tool.name, "test_tool")
        self.assertEqual(self.tool.description, "A test tool for testing")
        self.assertEqual(self.tool.function_type, "object")
        self.assertEqual(len(self.tool.properties), 2)
        self.assertEqual(len(self.tool.required), 1)
        self.assertEqual(self.tool.required[0], "param1")


class TestMCPTools(unittest.TestCase):
    """Test the MCPTools class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool1 = Tool(
            name="tool1",
            description="First test tool",
            function_type="object",
            properties={
                "param1": {"type": "string"}
            },
            required=["param1"]
        )
        
        self.tool2 = Tool(
            name="tool2",
            description="Second test tool",
            function_type="object",
            properties={
                "param2": {"type": "integer"}
            },
            required=["param2"]
        )
        
        # Test tuple format (internal_name, external_name), (internal_desc, external_desc), [None, schema_dict]
        self.tool_tuple = (
            ("internal_tool3", "tool3"),
            ("Internal description", "Third test tool"),
            [None, {
                "type": "object",
                "properties": {
                    "param3": {"type": "boolean"}
                },
                "required": ["param3"]
            }]
        )

    def test_add_single_tool(self):
        """Test adding a single tool."""
        tools = MCPTools()
        tools.add([self.tool1])
        self.assertEqual(len(tools.tools), 1)
        self.assertEqual(tools.tools["tool1"].name, "tool1")

    def test_add_multiple_tools(self):
        """Test adding multiple tools at once."""
        tools = MCPTools()
        tools.add([self.tool1, self.tool2])
        self.assertEqual(len(tools.tools), 2)
        self.assertEqual(tools.tools["tool1"].name, "tool1")
        self.assertEqual(tools.tools["tool2"].name, "tool2")

    def test_add_tuple_tool(self):
        """Test adding a tool in tuple format."""
        tools = MCPTools()
        tools.add([self.tool_tuple])
        self.assertEqual(len(tools.tools), 1)
        tool = tools.tools["tool3"]
        self.assertEqual(tool.name, "tool3")
        self.assertEqual(tool.description, "Third test tool")
        self.assertEqual(tool.function_type, "object")
        self.assertIn("param3", tool.properties)

    def test_add_invalid_tuple(self):
        """Test adding an invalid tuple."""
        tools = MCPTools()
        # Invalid schema list
        invalid_tuple = (
            ("internal_tool4", "tool4"),
            ("Internal description", "Fourth test tool"),
            [None]  # Missing schema dict
        )
        tools.add([invalid_tuple])
        # Should not add the invalid tool
        self.assertEqual(len(tools.tools), 0)

    def test_get_tool(self):
        """Test getting a tool by name."""
        tools = MCPTools()
        tools.add([self.tool1, self.tool2])
        
        # Valid tool
        tool = tools.get_tool("tool1")
        self.assertEqual(tool.name, "tool1")
        
        # Invalid tool
        nonexistent = tools.get_tool("nonexistent_tool")
        self.assertIsNone(nonexistent)

    def test_get_desc(self):
        """Test getting a tool description."""
        tools = MCPTools()
        tools.add([self.tool1])
        
        # Valid tool
        desc = tools.get_desc("tool1")
        self.assertEqual(desc, "First test tool")
        
        # Invalid tool
        nonexistent = tools.get_desc("nonexistent_tool")
        self.assertIsNone(nonexistent)

    def test_list_tools(self):
        """Test listing all tools."""
        tools = MCPTools()
        tools.add([self.tool1, self.tool2])
        
        tool_list = tools.list_tools()
        self.assertEqual(len(tool_list), 2)
        names = [t.name for t in tool_list]
        self.assertIn("tool1", names)
        self.assertIn("tool2", names)

    def test_remove_tool(self):
        """Test removing a tool."""
        tools = MCPTools()
        tools.add([self.tool1, self.tool2])
        self.assertEqual(len(tools.tools), 2)
        
        # Remove a tool
        tools.remove_tool("tool1")
        self.assertEqual(len(tools.tools), 1)
        self.assertNotIn("tool1", tools.tools)
        self.assertIn("tool2", tools.tools)
        
        # Removing non-existent tool should not raise error
        tools.remove_tool("nonexistent_tool")
        self.assertEqual(len(tools.tools), 1)


if __name__ == "__main__":
    unittest.main()