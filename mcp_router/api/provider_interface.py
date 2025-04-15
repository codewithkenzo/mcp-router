"""
Provider Interface for MCP Router.
Defines the interface for LLM providers that can be used with MCP Router.
"""

from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from abc import ABC, abstractmethod

class ProviderInterface(ABC):
    """
    Abstract base class for LLM provider interfaces.
    All provider implementations should inherit from this class.
    """
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the provider.
        
        Returns:
            str: The name of the provider.
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models for this provider.
        
        Returns:
            List[Dict[str, Any]]: A list of model information dictionaries.
        """
        pass
    
    @abstractmethod
    async def generate_text(self, 
                     prompt: str, 
                     system_prompt: Optional[str] = None,
                     model: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text using the provider's API.
        
        Args:
            prompt: The user prompt to generate text from.
            system_prompt: Optional system prompt to guide the generation.
            model: Optional model identifier to use for generation.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            
        Returns:
            Union[str, AsyncGenerator[str, None]]: Generated text or a stream of text chunks.
        """
        pass
    
    @abstractmethod
    async def get_token_count(self, text: str, model: Optional[str] = None) -> int:
        """
        Get the number of tokens in the given text for the specified model.
        
        Args:
            text: The text to count tokens for.
            model: Optional model identifier to use for token counting.
            
        Returns:
            int: The number of tokens in the text.
        """
        pass
    
    @abstractmethod
    def get_provider_config(self) -> Dict[str, Any]:
        """
        Get the configuration for this provider.
        
        Returns:
            Dict[str, Any]: The provider configuration.
        """
        pass
