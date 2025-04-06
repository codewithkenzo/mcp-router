#!/usr/bin/env python3
"""
Command-line interface for MCP Router.
Provides commands for managing MCP servers and interacting with OpenRouter.
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

# Add parent directory to path to import mcp_router
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_router import MCPRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_router_cli")

# Load environment variables
load_dotenv()

async def list_servers(args: argparse.Namespace) -> None:
    """List available and configured servers."""
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    if args.available:
        print("\nAvailable servers in registry:")
        available_servers = await router.list_available_servers()
        
        if not available_servers:
            print("  No servers found in registry.")
        else:
            for server_id, info in available_servers.items():
                description = info.get("description", "No description")
                source = info.get("source", "unknown")
                print(f"  - {server_id}: {description} (source: {source})")
    
    if args.configured:
        print("\nConfigured servers:")
        configured_servers = await router.list_configured_servers()
        
        if not configured_servers:
            print("  No servers configured.")
        else:
            for server_id, config in configured_servers.items():
                command = config.get("command", "")
                args_str = " ".join(config.get("args", []))
                print(f"  - {server_id}: {command} {args_str}")
    
    if args.running:
        print("\nRunning servers:")
        running_servers = await router.list_running_servers()
        
        if not running_servers:
            print("  No servers running.")
        else:
            for server_id, status in running_servers.items():
                running = "RUNNING" if status["running"] else "STOPPED"
                pid = status["pid"] or "N/A"
                uptime = f"{status['uptime']:.2f}s" if status.get("uptime") else "N/A"
                print(f"  - {server_id}: {running} (PID: {pid}, Uptime: {uptime})")
    
    await router.close()

async def install_server(args: argparse.Namespace) -> None:
    """Install an MCP server."""
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    print(f"Installing MCP server '{args.server_id}'...")
    success, output, config = await router.install_server(args.server_id)
    
    if success:
        print(f"Successfully installed server '{args.server_id}'.")
        print("\nServer configuration:")
        print(json.dumps(config, indent=2))
    else:
        print(f"Failed to install server '{args.server_id}': {output}")
    
    await router.close()

async def uninstall_server(args: argparse.Namespace) -> None:
    """Uninstall an MCP server."""
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    print(f"Uninstalling MCP server '{args.server_id}'...")
    success, output = await router.uninstall_server(args.server_id)
    
    if success:
        print(f"Successfully uninstalled server '{args.server_id}'.")
    else:
        print(f"Failed to uninstall server '{args.server_id}': {output}")
    
    await router.close()

async def start_server(args: argparse.Namespace) -> None:
    """Start an MCP server."""
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    print(f"Starting MCP server '{args.server_id}'...")
    success, error = await router.start_server(args.server_id)
    
    if success:
        print(f"Successfully started server '{args.server_id}'.")
    else:
        print(f"Failed to start server '{args.server_id}': {error}")
    
    await router.close()

async def stop_server(args: argparse.Namespace) -> None:
    """Stop an MCP server."""
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    print(f"Stopping MCP server '{args.server_id}'...")
    success, error = await router.stop_server(args.server_id, force=args.force)
    
    if success:
        print(f"Successfully stopped server '{args.server_id}'.")
    else:
        print(f"Failed to stop server '{args.server_id}': {error}")
    
    await router.close()

async def restart_server(args: argparse.Namespace) -> None:
    """Restart an MCP server."""
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    print(f"Restarting MCP server '{args.server_id}'...")
    success, error = await router.restart_server(args.server_id)
    
    if success:
        print(f"Successfully restarted server '{args.server_id}'.")
    else:
        print(f"Failed to restart server '{args.server_id}': {error}")
    
    await router.close()

async def query(args: argparse.Namespace) -> None:
    """Execute a query using OpenRouter and MCP servers."""
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    print(f"Executing query using model '{args.model}'...")
    if args.servers:
        print(f"Using servers: {', '.join(args.servers)}")
    else:
        print("No servers specified, using direct OpenRouter query.")
    
    result = await router.query(
        user_query=args.query,
        servers=args.servers,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    print("\nConversation:")
    for message in result["messages"]:
        role = message["role"]
        if role == "user":
            print(f"\nUser: {message['content']}")
        elif role == "assistant":
            print(f"\nAssistant: {message['content']}")
        elif role == "tool":
            print(f"\nTool result: {message['content']}")
    
    print(f"\nQuery completed with {result['tool_calls']} tool calls.")
    
    await router.close()

async def create_custom_server(args: argparse.Namespace) -> None:
    """Create a custom MCP server configuration."""
    router = MCPRouter(config_path=args.config, registry_path=args.registry)
    
    env = {}
    if args.env:
        for env_var in args.env:
            key, value = env_var.split("=", 1)
            env[key] = value
    
    print(f"Creating custom server '{args.server_id}'...")
    success, message = await router.create_custom_server(
        server_id=args.server_id,
        command=args.command,
        args=args.args,
        env=env
    )
    
    print(message)
    
    await router.close()

async def list_models(args: argparse.Namespace) -> None:
    """List available OpenRouter models."""
    router = MCPRouter()
    
    print("Fetching available models from OpenRouter...")
    try:
        models = router.list_openrouter_models()
        
        print(f"\nAvailable models ({len(models)}):")
        for model in models:
            print(f"  - {model.id}")
    except Exception as e:
        print(f"Error fetching models: {e}")
    
    await router.close()

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="MCP Router CLI")
    parser.add_argument("--config", help="Path to the MCP server config file", default="~/.mcp/config.json")
    parser.add_argument("--registry", help="Path to the MCP server registry file", default="~/.mcp/registry.json")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List servers
    list_parser = subparsers.add_parser("list", help="List MCP servers")
    list_parser.add_argument("--available", "-a", action="store_true", help="List available servers in registry")
    list_parser.add_argument("--configured", "-c", action="store_true", help="List configured servers")
    list_parser.add_argument("--running", "-r", action="store_true", help="List running servers")
    
    # Install server
    install_parser = subparsers.add_parser("install", help="Install an MCP server")
    install_parser.add_argument("server_id", help="Identifier of the server to install")
    
    # Uninstall server
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall an MCP server")
    uninstall_parser.add_argument("server_id", help="Identifier of the server to uninstall")
    
    # Start server
    start_parser = subparsers.add_parser("start", help="Start an MCP server")
    start_parser.add_argument("server_id", help="Identifier of the server to start")
    
    # Stop server
    stop_parser = subparsers.add_parser("stop", help="Stop an MCP server")
    stop_parser.add_argument("server_id", help="Identifier of the server to stop")
    stop_parser.add_argument("--force", "-f", action="store_true", help="Force stop the server")
    
    # Restart server
    restart_parser = subparsers.add_parser("restart", help="Restart an MCP server")
    restart_parser.add_argument("server_id", help="Identifier of the server to restart")
    
    # Query
    query_parser = subparsers.add_parser("query", help="Execute a query using OpenRouter and MCP servers")
    query_parser.add_argument("query", help="Query to execute")
    query_parser.add_argument("--servers", "-s", nargs="*", help="MCP server IDs to use")
    query_parser.add_argument("--model", "-m", help="OpenRouter model to use", default="meta-llama/llama-4-maverick:free")
    query_parser.add_argument("--temperature", "-t", type=float, help="Temperature for generation", default=0.7)
    query_parser.add_argument("--max-tokens", type=int, help="Maximum tokens to generate")
    
    # Create custom server
    custom_parser = subparsers.add_parser("create", help="Create a custom MCP server configuration")
    custom_parser.add_argument("server_id", help="Identifier for the server")
    custom_parser.add_argument("--command", "-c", required=True, help="Command to start the server")
    custom_parser.add_argument("--args", "-a", nargs="*", help="Command arguments")
    custom_parser.add_argument("--env", "-e", nargs="*", help="Environment variables (KEY=VALUE)")
    
    # List models
    models_parser = subparsers.add_parser("models", help="List available OpenRouter models")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        if not any([args.available, args.configured, args.running]):
            args.available = args.configured = args.running = True
        asyncio.run(list_servers(args))
    elif args.command == "install":
        asyncio.run(install_server(args))
    elif args.command == "uninstall":
        asyncio.run(uninstall_server(args))
    elif args.command == "start":
        asyncio.run(start_server(args))
    elif args.command == "stop":
        asyncio.run(stop_server(args))
    elif args.command == "restart":
        asyncio.run(restart_server(args))
    elif args.command == "query":
        asyncio.run(query(args))
    elif args.command == "create":
        asyncio.run(create_custom_server(args))
    elif args.command == "models":
        asyncio.run(list_models(args))

if __name__ == "__main__":
    main() 