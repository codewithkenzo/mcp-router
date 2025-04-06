"""
Playwright utilities for scraping and interacting with web content.
Uses the Playwright MCP server to automate browser interactions.
"""

import json
import logging
import os
import time
from typing import Dict, Any, List, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PlaywrightMCP:
    """
    Utility class for interacting with the Playwright MCP server.
    Uses the MCP Python SDK to communicate with the Playwright MCP server.
    """
    
    def __init__(self, mcp_client=None):
        """
        Initialize the Playwright MCP utility.
        
        Args:
            mcp_client: An initialized MCP client instance.
                        If None, will attempt to use a default client.
        """
        self.mcp_client = mcp_client
        self._last_snapshot = None
    
    async def _call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Call a tool on the Playwright MCP server.
        
        Args:
            tool_name: Name of the tool to call.
            args: Arguments for the tool.
            
        Returns:
            Result of the tool call.
            
        Raises:
            ValueError: If the MCP client is not initialized.
            RuntimeError: If the tool call fails.
        """
        if not self.mcp_client:
            raise ValueError("MCP client not initialized")
        
        # Find the Playwright MCP server
        servers = self.mcp_client.list_servers()
        playwright_server = None
        for server in servers:
            if "playwright" in server.lower():
                playwright_server = server
                break
        
        if not playwright_server:
            raise RuntimeError("Playwright MCP server not found")
        
        # Call the tool
        tool_name_full = f"mcp_playwright_browser_{tool_name}"
        try:
            return await self.mcp_client.call_tool(playwright_server, tool_name_full, args)
        except Exception as e:
            logger.error(f"Error calling Playwright tool {tool_name}: {str(e)}")
            raise RuntimeError(f"Failed to call Playwright tool {tool_name}: {str(e)}")
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to.
            
        Returns:
            Result of the navigation.
        """
        logger.info(f"Navigating to {url}")
        return await self._call_tool("navigate", {"url": url})
    
    async def snapshot(self) -> Dict[str, Any]:
        """
        Take an accessibility snapshot of the current page.
        
        Returns:
            Snapshot data.
        """
        result = await self._call_tool("snapshot", {"random_string": "snapshot"})
        self._last_snapshot = result
        return result
    
    async def click(self, element_ref: str, element_description: str) -> Dict[str, Any]:
        """
        Click on an element.
        
        Args:
            element_ref: Element reference from snapshot.
            element_description: Human-readable description of the element.
            
        Returns:
            Result of the click operation.
        """
        logger.info(f"Clicking on element: {element_description}")
        return await self._call_tool("click", {
            "ref": element_ref,
            "element": element_description
        })
    
    async def type_text(self, element_ref: str, element_description: str, text: str, submit: bool = False) -> Dict[str, Any]:
        """
        Type text into an element.
        
        Args:
            element_ref: Element reference from snapshot.
            element_description: Human-readable description of the element.
            text: Text to type.
            submit: Whether to press Enter after typing.
            
        Returns:
            Result of the type operation.
        """
        logger.info(f"Typing '{text}' into element: {element_description}")
        return await self._call_tool("type", {
            "ref": element_ref,
            "element": element_description,
            "text": text,
            "submit": submit
        })
    
    async def select_option(self, element_ref: str, element_description: str, values: List[str]) -> Dict[str, Any]:
        """
        Select options in a dropdown.
        
        Args:
            element_ref: Element reference from snapshot.
            element_description: Human-readable description of the element.
            values: Values to select.
            
        Returns:
            Result of the select operation.
        """
        logger.info(f"Selecting options {values} in element: {element_description}")
        return await self._call_tool("select_option", {
            "ref": element_ref,
            "element": element_description,
            "values": values
        })
    
    async def press_key(self, key: str) -> Dict[str, Any]:
        """
        Press a key.
        
        Args:
            key: Key to press.
            
        Returns:
            Result of the key press.
        """
        logger.info(f"Pressing key: {key}")
        return await self._call_tool("press_key", {"key": key})
    
    async def wait(self, seconds: float) -> Dict[str, Any]:
        """
        Wait for a specified time.
        
        Args:
            seconds: Time to wait in seconds.
            
        Returns:
            Result of the wait operation.
        """
        logger.info(f"Waiting for {seconds} seconds")
        return await self._call_tool("wait", {"time": seconds})
    
    async def take_screenshot(self, raw: bool = False) -> Dict[str, Any]:
        """
        Take a screenshot of the current page.
        
        Args:
            raw: Whether to return the raw PNG data.
            
        Returns:
            Screenshot data.
        """
        logger.info("Taking screenshot")
        return await self._call_tool("take_screenshot", {"raw": raw})
    
    async def go_back(self) -> Dict[str, Any]:
        """
        Go back to the previous page.
        
        Returns:
            Result of the operation.
        """
        logger.info("Going back to previous page")
        return await self._call_tool("go_back", {"random_string": "back"})
    
    async def go_forward(self) -> Dict[str, Any]:
        """
        Go forward to the next page.
        
        Returns:
            Result of the operation.
        """
        logger.info("Going forward to next page")
        return await self._call_tool("go_forward", {"random_string": "forward"})
    
    async def close(self) -> Dict[str, Any]:
        """
        Close the browser.
        
        Returns:
            Result of the operation.
        """
        logger.info("Closing browser")
        return await self._call_tool("close", {"random_string": "close"})
    
    async def save_as_pdf(self) -> Dict[str, Any]:
        """
        Save the current page as PDF.
        
        Returns:
            PDF data.
        """
        logger.info("Saving page as PDF")
        return await self._call_tool("save_as_pdf", {"random_string": "pdf"})
    
    def find_element(self, snapshot: Dict[str, Any], predicate: Callable[[Dict[str, Any]], bool]) -> Optional[Dict[str, Any]]:
        """
        Find an element in a snapshot using a predicate function.
        
        Args:
            snapshot: Snapshot data.
            predicate: Function that returns True for the desired element.
            
        Returns:
            Element data or None if not found.
        """
        def _search_node(node):
            if predicate(node):
                return node
            
            for child in node.get("children", []):
                result = _search_node(child)
                if result:
                    return result
            
            return None
        
        root = snapshot.get("tree", {})
        return _search_node(root)
    
    def find_elements(self, snapshot: Dict[str, Any], predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        """
        Find all elements in a snapshot that match a predicate function.
        
        Args:
            snapshot: Snapshot data.
            predicate: Function that returns True for matching elements.
            
        Returns:
            List of matching element data.
        """
        results = []
        
        def _search_node(node):
            if predicate(node):
                results.append(node)
            
            for child in node.get("children", []):
                _search_node(child)
        
        root = snapshot.get("tree", {})
        _search_node(root)
        return results
    
    def find_element_by_text(self, snapshot: Dict[str, Any], text: str, exact: bool = False) -> Optional[Dict[str, Any]]:
        """
        Find an element in a snapshot by its text content.
        
        Args:
            snapshot: Snapshot data.
            text: Text to search for.
            exact: Whether to match the exact text or a substring.
            
        Returns:
            Element data or None if not found.
        """
        def predicate(node):
            node_text = node.get("text", "")
            if exact:
                return node_text == text
            else:
                return text.lower() in node_text.lower()
        
        return self.find_element(snapshot, predicate)
    
    def find_element_by_role(self, snapshot: Dict[str, Any], role: str, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find an element in a snapshot by its role.
        
        Args:
            snapshot: Snapshot data.
            role: ARIA role to search for.
            name: Optional name (accessible name) of the element.
            
        Returns:
            Element data or None if not found.
        """
        def predicate(node):
            if node.get("role") != role:
                return False
            
            if name is not None:
                node_name = node.get("name", "")
                return name.lower() in node_name.lower()
            
            return True
        
        return self.find_element(snapshot, predicate)
    
    def extract_text_content(self, snapshot: Dict[str, Any]) -> str:
        """
        Extract all text content from a snapshot.
        
        Args:
            snapshot: Snapshot data.
            
        Returns:
            Concatenated text content.
        """
        text_content = []
        
        def _extract_text(node):
            if "text" in node and node["text"].strip():
                text_content.append(node["text"].strip())
            
            for child in node.get("children", []):
                _extract_text(child)
        
        root = snapshot.get("tree", {})
        _extract_text(root)
        return "\n".join(text_content)
    
    def extract_links(self, snapshot: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract all links from a snapshot.
        
        Args:
            snapshot: Snapshot data.
            
        Returns:
            List of dictionaries with link info.
        """
        links = []
        
        def _find_links(node):
            if node.get("role") == "link" and "url" in node:
                links.append({
                    "text": node.get("text", ""),
                    "url": node["url"],
                    "ref": node.get("ref", "")
                })
            
            for child in node.get("children", []):
                _find_links(child)
        
        root = snapshot.get("tree", {})
        _find_links(root)
        return links
    
    def extract_form_elements(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all form elements from a snapshot.
        
        Args:
            snapshot: Snapshot data.
            
        Returns:
            List of dictionaries with form element info.
        """
        form_elements = []
        form_roles = {"textbox", "button", "checkbox", "radio", "combobox", "listbox", "switch"}
        
        def _find_form_elements(node):
            role = node.get("role", "")
            if role in form_roles:
                form_elements.append({
                    "role": role,
                    "name": node.get("name", ""),
                    "text": node.get("text", ""),
                    "ref": node.get("ref", ""),
                    "checked": node.get("checked", None),
                    "value": node.get("value", None)
                })
            
            for child in node.get("children", []):
                _find_form_elements(child)
        
        root = snapshot.get("tree", {})
        _find_form_elements(root)
        return form_elements


# Example usage (async context required)
"""
async def example():
    from mcp import MCPClient
    
    # Initialize MCP client
    client = MCPClient()
    await client.connect()
    
    # Initialize Playwright utility
    pw = PlaywrightMCP(client)
    
    # Navigate to a page
    await pw.navigate("https://example.com")
    
    # Take a snapshot
    snapshot = await pw.snapshot()
    
    # Extract text content
    text = pw.extract_text_content(snapshot)
    print(f"Page content:\n{text}")
    
    # Find and click a link
    links = pw.extract_links(snapshot)
    if links:
        link = links[0]
        await pw.click(link["ref"], f"Link to {link['url']}")
    
    # Close the browser
    await pw.close()
"""
