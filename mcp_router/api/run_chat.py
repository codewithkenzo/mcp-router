#!/usr/bin/env python3
"""
Run the MCP Router Chat Interface.
"""

import os
import argparse
import logging
from pathlib import Path

from .api_manager import APIManager
from .chat import ChatInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Run the MCP Router Chat Interface.
    """
    parser = argparse.ArgumentParser(description="MCP Router Chat Interface")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--api-dir", help="Path to the TypeScript API directory")
    
    args = parser.parse_args()
    
    # Determine API directory
    api_dir = args.api_dir
    if not api_dir:
        # Try to find the API directory relative to this file
        api_dir = str(Path(__file__).parent.parent.parent / "api")
        if not os.path.exists(api_dir):
            logger.warning(f"TypeScript API directory not found at {api_dir}")
            logger.warning("Please specify the API directory with --api-dir")
    
    # Initialize API manager
    api_manager = APIManager(api_dir=api_dir)
    
    # Initialize chat interface
    chat_interface = ChatInterface(api_manager=api_manager, host=args.host, port=args.port)
    
    # Run the chat interface
    logger.info(f"Starting MCP Router Chat Interface on http://{args.host}:{args.port}")
    chat_interface.run()

if __name__ == "__main__":
    main()
