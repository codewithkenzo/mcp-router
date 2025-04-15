"""
API Manager for MCP Router.
Manages the integration between Python MCP Router and TypeScript API providers.
"""

import os
import json
import asyncio
import subprocess
import logging
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from pathlib import Path

from .provider_interface import ProviderInterface

logger = logging.getLogger(__name__)

class APIManager:
    """
    Manages the integration between Python MCP Router and TypeScript API providers.
    Provides methods for interacting with various LLM providers through the TypeScript API.
    """
    
    def __init__(self, api_dir: Optional[str] = None):
        """
        Initialize the API Manager.
        
        Args:
            api_dir: Optional path to the TypeScript API directory.
                    If not provided, will use the default location.
        """
        self.api_dir = api_dir or str(Path(__file__).parent.parent.parent / "api")
        self.providers: Dict[str, Any] = {}
        self.provider_configs: Dict[str, Dict[str, Any]] = {}
        self._load_provider_configs()
        
    def _load_provider_configs(self) -> None:
        """
        Load provider configurations from the TypeScript API directory.
        """
        try:
            # Check if the TypeScript API is installed
            if not os.path.exists(self.api_dir):
                logger.warning(f"TypeScript API directory not found at {self.api_dir}")
                return
                
            # Get the list of provider files
            provider_files = [f for f in os.listdir(os.path.join(self.api_dir, "providers")) 
                             if f.endswith(".ts") and not f.startswith("_")]
            
            # Extract provider names
            for provider_file in provider_files:
                provider_name = provider_file.replace(".ts", "")
                self.provider_configs[provider_name] = {
                    "name": provider_name,
                    "file": provider_file,
                    "path": os.path.join(self.api_dir, "providers", provider_file)
                }
                
            logger.info(f"Loaded {len(self.provider_configs)} provider configurations")
        except Exception as e:
            logger.error(f"Error loading provider configurations: {e}")
    
    def get_available_providers(self) -> List[str]:
        """
        Get a list of available provider names.
        
        Returns:
            List[str]: A list of provider names.
        """
        return list(self.provider_configs.keys())
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific provider.
        
        Args:
            provider_name: The name of the provider.
            
        Returns:
            Optional[Dict[str, Any]]: The provider configuration, or None if not found.
        """
        return self.provider_configs.get(provider_name)
    
    async def call_typescript_api(self, 
                           provider: str, 
                           method: str, 
                           params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a method in the TypeScript API.
        
        Args:
            provider: The provider name.
            method: The method name to call.
            params: The parameters to pass to the method.
            
        Returns:
            Dict[str, Any]: The response from the TypeScript API.
        """
        # Create a temporary JSON file with the parameters
        params_file = os.path.join(os.path.dirname(__file__), "temp_params.json")
        with open(params_file, "w") as f:
            json.dump({
                "provider": provider,
                "method": method,
                "params": params
            }, f)
        
        try:
            # Call the TypeScript API using Node.js
            cmd = [
                "node", 
                os.path.join(self.api_dir, "cli.js"),
                "--params", params_file
            ]
            
            # Run the command and capture the output
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Error calling TypeScript API: {stderr.decode()}")
                raise Exception(f"Error calling TypeScript API: {stderr.decode()}")
            
            # Parse the JSON response
            response = json.loads(stdout.decode())
            return response
        finally:
            # Clean up the temporary file
            if os.path.exists(params_file):
                os.remove(params_file)
    
    async def generate_text(self,
                     provider: str,
                     prompt: str,
                     system_prompt: Optional[str] = None,
                     model: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text using a specific provider.
        
        Args:
            provider: The provider name.
            prompt: The user prompt to generate text from.
            system_prompt: Optional system prompt to guide the generation.
            model: Optional model identifier to use for generation.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            
        Returns:
            Union[str, AsyncGenerator[str, None]]: Generated text or a stream of text chunks.
        """
        params = {
            "prompt": prompt,
            "systemPrompt": system_prompt,
            "model": model,
            "temperature": temperature,
            "maxTokens": max_tokens,
            "stream": stream
        }
        
        if stream:
            return self._stream_text(provider, params)
        else:
            response = await self.call_typescript_api(provider, "generateText", params)
            return response.get("text", "")
    
    async def _stream_text(self, provider: str, params: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Stream text from a provider.
        
        Args:
            provider: The provider name.
            params: The parameters for text generation.
            
        Yields:
            str: Text chunks as they are generated.
        """
        # Create a temporary JSON file with the parameters
        params_file = os.path.join(os.path.dirname(__file__), "temp_stream_params.json")
        with open(params_file, "w") as f:
            json.dump({
                "provider": provider,
                "method": "generateText",
                "params": params
            }, f)
        
        try:
            # Call the TypeScript API using Node.js with streaming
            cmd = [
                "node", 
                os.path.join(self.api_dir, "cli.js"),
                "--params", params_file,
                "--stream"
            ]
            
            # Run the command and stream the output
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Read and yield output line by line
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                try:
                    chunk = json.loads(line.decode().strip())
                    yield chunk.get("text", "")
                except json.JSONDecodeError:
                    # Skip lines that aren't valid JSON
                    continue
            
            # Check for errors
            if process.returncode and process.returncode != 0:
                stderr = await process.stderr.read()
                logger.error(f"Error streaming from TypeScript API: {stderr.decode()}")
                raise Exception(f"Error streaming from TypeScript API: {stderr.decode()}")
                
        finally:
            # Clean up the temporary file
            if os.path.exists(params_file):
                os.remove(params_file)
    
    async def get_token_count(self, provider: str, text: str, model: Optional[str] = None) -> int:
        """
        Get the number of tokens in the given text for the specified model.
        
        Args:
            provider: The provider name.
            text: The text to count tokens for.
            model: Optional model identifier to use for token counting.
            
        Returns:
            int: The number of tokens in the text.
        """
        params = {
            "text": text,
            "model": model
        }
        
        response = await self.call_typescript_api(provider, "getTokenCount", params)
        return response.get("count", 0)
    
    async def get_available_models(self, provider: str) -> List[Dict[str, Any]]:
        """
        Get a list of available models for a specific provider.
        
        Args:
            provider: The provider name.
            
        Returns:
            List[Dict[str, Any]]: A list of model information dictionaries.
        """
        response = await self.call_typescript_api(provider, "getAvailableModels", {})
        return response.get("models", [])
