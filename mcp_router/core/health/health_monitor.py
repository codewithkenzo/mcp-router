"""
Health Monitor Module

This module provides a health monitoring system for MCP servers,
allowing the system to track the health and status of servers.
"""

import os
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class HealthMonitor:
    """
    Health monitoring system for MCP servers.
    
    This class provides functionality to monitor the health of MCP servers
    and update their status in the registry.
    """
    
    def __init__(self, 
                 server_registry, 
                 metadata_store=None, 
                 check_interval: int = 300):
        """
        Initialize the health monitor.
        
        Args:
            server_registry: ServerRegistry instance
            metadata_store: Optional MetadataStore instance
            check_interval: Interval between health checks in seconds (default: 300)
        """
        self.server_registry = server_registry
        self.metadata_store = metadata_store
        self.check_interval = check_interval
        self.running = False
        self._task = None
    
    async def start_monitoring(self):
        """Start the health monitoring background task."""
        if self.running:
            logger.warning("Health monitor is already running")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop the health monitoring background task."""
        if not self.running:
            logger.warning("Health monitor is not running")
            return
        
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop that periodically checks server health."""
        try:
            while self.running:
                await self.check_all_servers()
                await asyncio.sleep(self.check_interval)
        except asyncio.CancelledError:
            logger.info("Health monitoring loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in health monitoring loop: {e}")
            self.running = False
    
    async def check_all_servers(self):
        """Check the health of all registered servers."""
        logger.info("Checking health of all servers")
        
        server_ids = list(self.server_registry.get_all_servers().keys())
        for server_id in server_ids:
            try:
                await self.check_server_health(server_id)
            except Exception as e:
                logger.error(f"Error checking health of server {server_id}: {e}")
    
    async def check_server_health(self, server_id: str):
        """
        Check the health of a specific server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            True if the server is healthy, False otherwise
        """
        logger.debug(f"Checking health of server: {server_id}")
        
        # Get server configuration
        server_config = self.server_registry.get_server_config(server_id)
        if not server_config:
            logger.warning(f"Server {server_id} not found in registry")
            return False
        
        # Perform health check
        start_time = time.time()
        try:
            # Implement actual health check logic here
            # This could involve:
            # 1. Trying to connect to the server
            # 2. Calling a simple tool to verify functionality
            # 3. Checking if the server process is running
            
            # For now, we'll just simulate a health check
            healthy = await self._simulate_health_check(server_id, server_config)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update server health status
            status = "online" if healthy else "offline"
            self.server_registry.update_server_health(server_id, status, response_time)
            
            # Update metadata store if available
            if self.metadata_store:
                self.metadata_store.update_server_health(server_id, status, response_time)
            
            logger.info(f"Server {server_id} health check: {status}, response time: {response_time:.3f}s")
            return healthy
        
        except Exception as e:
            # Update server health status to error
            self.server_registry.update_server_health(server_id, "error")
            
            # Update metadata store if available
            if self.metadata_store:
                self.metadata_store.update_server_health(server_id, "error")
            
            logger.error(f"Error checking health of server {server_id}: {e}")
            return False
    
    async def _simulate_health_check(self, server_id: str, server_config: Dict[str, Any]) -> bool:
        """
        Simulate a health check for a server.
        
        In a real implementation, this would be replaced with actual health check logic.
        
        Args:
            server_id: Unique identifier for the server
            server_config: Server configuration
            
        Returns:
            True if the server is healthy, False otherwise
        """
        # For demonstration purposes, we'll just return True most of the time
        # with occasional failures to simulate real-world behavior
        import random
        
        # 90% chance of success
        return random.random() < 0.9
    
    async def get_server_health_status(self, server_id: str) -> Dict[str, Any]:
        """
        Get the health status of a specific server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            Dictionary containing health status information
        """
        # Get health status from registry
        health_status = self.server_registry.get_server_health(server_id)
        
        # If metadata store is available, get additional information
        if self.metadata_store:
            try:
                usage_stats = self.metadata_store.get_server_usage_stats(server_id)
                if health_status and usage_stats:
                    health_status.update(usage_stats)
            except Exception as e:
                logger.error(f"Error getting usage stats for server {server_id}: {e}")
        
        return health_status or {}
    
    async def get_all_server_health_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status for all servers.
        
        Returns:
            Dictionary of server_id to health status
        """
        # Get all health statuses from registry
        health_statuses = self.server_registry.get_all_server_health()
        
        # If metadata store is available, get additional information
        if self.metadata_store:
            for server_id in health_statuses.keys():
                try:
                    usage_stats = self.metadata_store.get_server_usage_stats(server_id)
                    if usage_stats:
                        health_statuses[server_id].update(usage_stats)
                except Exception as e:
                    logger.error(f"Error getting usage stats for server {server_id}: {e}")
        
        return health_statuses
