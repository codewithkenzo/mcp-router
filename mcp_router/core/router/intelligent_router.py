"""
Intelligent Router Module

This module provides an intelligent routing system for MCP queries,
using LLMs to analyze queries and determine the most appropriate MCP servers.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class IntelligentRouter:
    """
    Intelligent router for MCP queries.
    
    This class analyzes user queries and determines the most appropriate
    MCP servers to handle them based on capabilities and metadata.
    """
    
    def __init__(self, 
                 server_registry, 
                 metadata_store, 
                 openrouter_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None):
        """
        Initialize the intelligent router.
        
        Args:
            server_registry: ServerRegistry instance
            metadata_store: MetadataStore instance
            openrouter_api_key: Optional API key for OpenRouter
            openai_api_key: Optional API key for OpenAI
            anthropic_api_key: Optional API key for Anthropic
        """
        self.server_registry = server_registry
        self.metadata_store = metadata_store
        self.openrouter_api_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY")
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        # Initialize LLM client if API keys are available
        self.llm_client = None
        if self.openrouter_api_key or self.openai_api_key or self.anthropic_api_key:
            self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """Initialize the LLM client based on available API keys."""
        try:
            # Try to import LLM libraries
            if self.openai_api_key:
                try:
                    from openai import OpenAI
                    self.llm_client = OpenAI(api_key=self.openai_api_key)
                    logger.info("Initialized OpenAI client for query analysis")
                except ImportError:
                    logger.warning("OpenAI package not installed, falling back to other providers")
            
            if self.llm_client is None and self.anthropic_api_key:
                try:
                    from anthropic import Anthropic
                    self.llm_client = Anthropic(api_key=self.anthropic_api_key)
                    logger.info("Initialized Anthropic client for query analysis")
                except ImportError:
                    logger.warning("Anthropic package not installed, falling back to other providers")
            
            if self.llm_client is None and self.openrouter_api_key:
                try:
                    import requests
                    # Using requests directly for OpenRouter
                    self.llm_client = "openrouter"
                    logger.info("Using OpenRouter for query analysis")
                except ImportError:
                    logger.warning("Requests package not installed, cannot use OpenRouter")
        
        except Exception as e:
            logger.error(f"Error initializing LLM client: {e}")
            self.llm_client = None
    
    async def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze a user query to determine required capabilities.
        
        Args:
            user_query: The user's query
            
        Returns:
            Dictionary containing analysis results
        """
        # If no LLM client is available, use keyword-based analysis
        if self.llm_client is None:
            return self._keyword_analysis(user_query)
        
        try:
            # Use LLM to analyze the query
            if isinstance(self.llm_client, str) and self.llm_client == "openrouter":
                return await self._analyze_with_openrouter(user_query)
            else:
                # Determine the type of LLM client and use appropriate method
                client_type = self.llm_client.__class__.__name__
                if "OpenAI" in client_type:
                    return await self._analyze_with_openai(user_query)
                elif "Anthropic" in client_type:
                    return await self._analyze_with_anthropic(user_query)
                else:
                    # Fallback to keyword analysis
                    return self._keyword_analysis(user_query)
        except Exception as e:
            logger.error(f"Error analyzing query with LLM: {e}")
            # Fallback to keyword analysis
            return self._keyword_analysis(user_query)
    
    def _keyword_analysis(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze a user query using keyword matching.
        
        Args:
            user_query: The user's query
            
        Returns:
            Dictionary containing analysis results
        """
        # Extract keywords from the query
        keywords = [word.lower() for word in user_query.split() if len(word) > 3]
        
        # Get all capabilities from the registry
        all_capabilities = set()
        for server_id, capabilities in self.server_registry.server_capabilities.items():
            all_capabilities.update(capabilities)
        
        # Match keywords to capabilities
        matched_capabilities = set()
        for capability in all_capabilities:
            capability_lower = capability.lower()
            for keyword in keywords:
                if keyword in capability_lower:
                    matched_capabilities.add(capability)
                    break
        
        return {
            "query": user_query,
            "required_capabilities": list(matched_capabilities),
            "confidence": 0.5,  # Lower confidence for keyword-based analysis
            "analysis_method": "keyword"
        }
    
    async def _analyze_with_openai(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze a user query using OpenAI.
        
        Args:
            user_query: The user's query
            
        Returns:
            Dictionary containing analysis results
        """
        # Get all capabilities from the registry
        all_capabilities = set()
        for server_id, capabilities in self.server_registry.server_capabilities.items():
            all_capabilities.update(capabilities)
        
        # Create a prompt for the LLM
        prompt = f"""
        You are an expert system that analyzes user queries and determines which capabilities are required to fulfill them.
        
        Available capabilities:
        {', '.join(all_capabilities)}
        
        User query: {user_query}
        
        Please analyze the query and determine which capabilities are required to fulfill it.
        Return your response as a JSON object with the following structure:
        {{
            "required_capabilities": ["capability1", "capability2", ...],
            "confidence": 0.0 to 1.0,
            "reasoning": "Your reasoning for selecting these capabilities"
        }}
        
        Only include capabilities from the list provided above. If none of the capabilities match, return an empty list.
        """
        
        try:
            response = await asyncio.to_thread(
                self.llm_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    # Validate the result
                    if "required_capabilities" not in result:
                        result["required_capabilities"] = []
                    if "confidence" not in result:
                        result["confidence"] = 0.7
                    
                    # Add analysis method
                    result["analysis_method"] = "openai"
                    result["query"] = user_query
                    
                    return result
                else:
                    raise ValueError("No JSON found in response")
            except Exception as e:
                logger.error(f"Error parsing OpenAI response: {e}")
                logger.error(f"Response content: {content}")
                return {
                    "query": user_query,
                    "required_capabilities": [],
                    "confidence": 0.0,
                    "analysis_method": "openai_failed",
                    "error": str(e)
                }
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return {
                "query": user_query,
                "required_capabilities": [],
                "confidence": 0.0,
                "analysis_method": "openai_failed",
                "error": str(e)
            }
    
    async def _analyze_with_anthropic(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze a user query using Anthropic.
        
        Args:
            user_query: The user's query
            
        Returns:
            Dictionary containing analysis results
        """
        # Get all capabilities from the registry
        all_capabilities = set()
        for server_id, capabilities in self.server_registry.server_capabilities.items():
            all_capabilities.update(capabilities)
        
        # Create a prompt for the LLM
        prompt = f"""
        You are an expert system that analyzes user queries and determines which capabilities are required to fulfill them.
        
        Available capabilities:
        {', '.join(all_capabilities)}
        
        User query: {user_query}
        
        Please analyze the query and determine which capabilities are required to fulfill it.
        Return your response as a JSON object with the following structure:
        {{
            "required_capabilities": ["capability1", "capability2", ...],
            "confidence": 0.0 to 1.0,
            "reasoning": "Your reasoning for selecting these capabilities"
        }}
        
        Only include capabilities from the list provided above. If none of the capabilities match, return an empty list.
        """
        
        try:
            response = await asyncio.to_thread(
                self.llm_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response
            content = response.content[0].text
            
            # Extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    # Validate the result
                    if "required_capabilities" not in result:
                        result["required_capabilities"] = []
                    if "confidence" not in result:
                        result["confidence"] = 0.7
                    
                    # Add analysis method
                    result["analysis_method"] = "anthropic"
                    result["query"] = user_query
                    
                    return result
                else:
                    raise ValueError("No JSON found in response")
            except Exception as e:
                logger.error(f"Error parsing Anthropic response: {e}")
                logger.error(f"Response content: {content}")
                return {
                    "query": user_query,
                    "required_capabilities": [],
                    "confidence": 0.0,
                    "analysis_method": "anthropic_failed",
                    "error": str(e)
                }
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            return {
                "query": user_query,
                "required_capabilities": [],
                "confidence": 0.0,
                "analysis_method": "anthropic_failed",
                "error": str(e)
            }
    
    async def _analyze_with_openrouter(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze a user query using OpenRouter.
        
        Args:
            user_query: The user's query
            
        Returns:
            Dictionary containing analysis results
        """
        # Get all capabilities from the registry
        all_capabilities = set()
        for server_id, capabilities in self.server_registry.server_capabilities.items():
            all_capabilities.update(capabilities)
        
        # Create a prompt for the LLM
        prompt = f"""
        You are an expert system that analyzes user queries and determines which capabilities are required to fulfill them.
        
        Available capabilities:
        {', '.join(all_capabilities)}
        
        User query: {user_query}
        
        Please analyze the query and determine which capabilities are required to fulfill it.
        Return your response as a JSON object with the following structure:
        {{
            "required_capabilities": ["capability1", "capability2", ...],
            "confidence": 0.0 to 1.0,
            "reasoning": "Your reasoning for selecting these capabilities"
        }}
        
        Only include capabilities from the list provided above. If none of the capabilities match, return an empty list.
        """
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 500
            }
            
            response = await asyncio.to_thread(
                requests.post,
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise ValueError(f"OpenRouter API returned status code {response.status_code}: {response.text}")
            
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            
            # Extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    # Validate the result
                    if "required_capabilities" not in result:
                        result["required_capabilities"] = []
                    if "confidence" not in result:
                        result["confidence"] = 0.7
                    
                    # Add analysis method
                    result["analysis_method"] = "openrouter"
                    result["query"] = user_query
                    
                    return result
                else:
                    raise ValueError("No JSON found in response")
            except Exception as e:
                logger.error(f"Error parsing OpenRouter response: {e}")
                logger.error(f"Response content: {content}")
                return {
                    "query": user_query,
                    "required_capabilities": [],
                    "confidence": 0.0,
                    "analysis_method": "openrouter_failed",
                    "error": str(e)
                }
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return {
                "query": user_query,
                "required_capabilities": [],
                "confidence": 0.0,
                "analysis_method": "openrouter_failed",
                "error": str(e)
            }
    
    async def select_servers(self, user_query: str) -> List[str]:
        """
        Select appropriate servers based on user query.
        
        Args:
            user_query: The user's query
            
        Returns:
            List of server IDs that can handle the query
        """
        # Analyze the query to determine required capabilities
        analysis = await self.analyze_query(user_query)
        required_capabilities = analysis.get("required_capabilities", [])
        
        # Get servers that match the required capabilities
        if required_capabilities:
            # Try to find servers that match all capabilities
            candidate_servers = self.server_registry.get_servers_by_capabilities(
                required_capabilities, require_all=True
            )
            
            # If no servers match all capabilities, try to find servers that match any capability
            if not candidate_servers:
                candidate_servers = self.server_registry.get_servers_by_capabilities(
                    required_capabilities, require_all=False
                )
        else:
            # If no capabilities were identified, fall back to metadata-based search
            candidate_servers = self.metadata_store.get_servers_for_task(user_query)
        
        # If still no servers found, return all online servers
        if not candidate_servers:
            candidate_servers = self.server_registry.get_online_servers()
        
        return candidate_servers
    
    def get_confidence_score(self) -> float:
        """
        Get the confidence score for the last routing decision.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # This is a placeholder; in a real implementation, you would track
        # the confidence score from the last analysis
        return 0.7
