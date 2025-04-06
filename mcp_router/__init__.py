"""
MCP Router package.
Extends Dolphin-MCP with OpenRouter API capabilities and replicates key HyperChat backend features.
"""

__version__ = "0.1.0"

from .main import MCPRouter
from .core.openrouter import OpenRouterClient
from .core.server_manager import MCPServerManager
from .server_management.config import MCPServerConfig
from .server_management.installer import MCPServerInstaller
from .server_management.lifecycle import MCPServerLifecycle
from .utils.playwright_utils import PlaywrightMCP

__all__ = [
    "MCPRouter",
    "OpenRouterClient",
    "MCPServerManager",
    "MCPServerConfig",
    "MCPServerInstaller",
    "MCPServerLifecycle",
    "PlaywrightMCP",
]
