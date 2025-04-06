"""
OpenRouter API integration for Dolphin-MCP.
Uses the OpenAI client library to interact with OpenRouter's API.
"""

import os
from typing import Dict, List, Any, Optional, Union
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenRouterClient:
    """Client for interacting with OpenRouter API using OpenAI's SDK."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. If None, loads from OPENROUTER_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass api_key.")
        
        # Configure OpenAI client for OpenRouter
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models on OpenRouter.
        
        Returns:
            List of model information dictionaries.
        """
        response = self.client.models.list()
        return response.data
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "anthropic/claude-3-5-sonnet",
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Union[Dict[str, Any], Any]:
        """
        Generate a chat completion using OpenRouter.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: Model identifier (e.g., 'anthropic/claude-3-5-sonnet').
            tools: Optional list of tool definitions for function calling.
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum tokens to generate.
            stream: Whether to stream the response.
            
        Returns:
            Completion response object.
        """
        # Format model name for OpenRouter if not already formatted
        if '/' not in model:
            model = f"openrouter/{model}"
        
        # Prepare parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        if tools:
            params["tools"] = tools
        
        # Make the API call
        if stream:
            return self.client.chat.completions.create(**params, stream=True)
        else:
            return self.client.chat.completions.create(**params)
    
    def execute_tool_call(
        self,
        messages: List[Dict[str, str]],
        tool_call: Dict[str, Any],
        tool_result: Any,
        model: str = "anthropic/claude-3-5-sonnet",
    ) -> Dict[str, Any]:
        """
        Execute a tool call and continue the conversation.
        
        Args:
            messages: The conversation history.
            tool_call: The tool call from the assistant.
            tool_result: The result of the tool execution.
            model: Model to use for the followup.
            
        Returns:
            Updated completion response.
        """
        # Add the tool call and result to the messages
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tool_call.get("id", "call_12345"),
                    "type": "function",
                    "function": {
                        "name": tool_call.get("function", {}).get("name", ""),
                        "arguments": tool_call.get("function", {}).get("arguments", "{}")
                    }
                }
            ]
        })
        
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.get("id", "call_12345"),
            "content": str(tool_result)
        })
        
        # Get a new response with the updated context
        return self.chat_completion(messages, model=model)


# Example usage
if __name__ == "__main__":
    client = OpenRouterClient()
    models = client.list_models()
    print(f"Available models: {len(models)}")
    
    response = client.chat_completion(
        messages=[{"role": "user", "content": "Hello, who are you?"}],
        model="anthropic/claude-3-5-sonnet",
    )
    
    print(response.choices[0].message.content)
