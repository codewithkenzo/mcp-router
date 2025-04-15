"""
Plugin Configuration Module

This module provides utilities for loading and managing plugin configurations.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PluginConfig:
    """
    Configuration manager for plugins.
    
    This class handles loading, saving, and managing configuration
    for plugins in the MCP Router system.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the plugin configuration manager.
        
        Args:
            config_dir: Optional directory for plugin configurations
        """
        self.config_dir = config_dir or os.path.expanduser("~/.mcp_router/plugin_configs")
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Dictionary of loaded configurations
        self.configs: Dict[str, Dict[str, Any]] = {}
    
    def load_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Load configuration for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dictionary containing plugin configuration
        """
        # Check if config is already loaded
        if plugin_name in self.configs:
            return self.configs[plugin_name]
        
        # Construct config file path
        config_file = os.path.join(self.config_dir, f"{plugin_name}.json")
        
        # Load config if it exists
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                self.configs[plugin_name] = config
                logger.info(f"Loaded configuration for plugin: {plugin_name}")
                return config
            except Exception as e:
                logger.error(f"Error loading configuration for plugin {plugin_name}: {e}")
                # Return empty config
                self.configs[plugin_name] = {}
                return {}
        else:
            # Create empty config
            self.configs[plugin_name] = {}
            logger.info(f"Created empty configuration for plugin: {plugin_name}")
            return {}
    
    def save_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Save configuration for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            config: Configuration dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        # Update in-memory config
        self.configs[plugin_name] = config
        
        # Construct config file path
        config_file = os.path.join(self.config_dir, f"{plugin_name}.json")
        
        # Save config to file
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved configuration for plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration for plugin {plugin_name}: {e}")
            return False
    
    def update_config(self, plugin_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update configuration for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            updates: Dictionary of configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        # Load current config
        config = self.load_config(plugin_name)
        
        # Apply updates
        config.update(updates)
        
        # Save updated config
        return self.save_config(plugin_name, config)
    
    def get_config_value(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            key: Configuration key to get
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        config = self.load_config(plugin_name)
        return config.get(key, default)
    
    def set_config_value(self, plugin_name: str, key: str, value: Any) -> bool:
        """
        Set a specific configuration value for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            key: Configuration key to set
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        # Load current config
        config = self.load_config(plugin_name)
        
        # Set value
        config[key] = value
        
        # Save updated config
        return self.save_config(plugin_name, config)
    
    def delete_config(self, plugin_name: str) -> bool:
        """
        Delete configuration for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if successful, False otherwise
        """
        # Remove from in-memory configs
        if plugin_name in self.configs:
            del self.configs[plugin_name]
        
        # Construct config file path
        config_file = os.path.join(self.config_dir, f"{plugin_name}.json")
        
        # Delete config file if it exists
        if os.path.exists(config_file):
            try:
                os.remove(config_file)
                logger.info(f"Deleted configuration for plugin: {plugin_name}")
                return True
            except Exception as e:
                logger.error(f"Error deleting configuration for plugin {plugin_name}: {e}")
                return False
        else:
            # Config file doesn't exist, consider it a success
            return True
