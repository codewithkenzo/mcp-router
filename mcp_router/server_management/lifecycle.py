"""
MCP server lifecycle management.
Handles starting, stopping, and checking the status of MCP servers.
"""

import os
import signal
import subprocess
import time
import psutil
from typing import Dict, Any, Optional, Tuple, List
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerLifecycle:
    """Manages the lifecycle of MCP servers."""
    
    def __init__(self, pid_dir: str = "~/.mcp/pids"):
        """
        Initialize the lifecycle manager.
        
        Args:
            pid_dir: Directory to store PID files.
        """
        self.pid_dir = os.path.expanduser(pid_dir)
        os.makedirs(self.pid_dir, exist_ok=True)
        self.active_processes: Dict[str, subprocess.Popen] = {}
    
    def _get_pid_file(self, server_id: str) -> str:
        """
        Get the path to the PID file for a server.
        
        Args:
            server_id: Server identifier.
            
        Returns:
            Path to the PID file.
        """
        return os.path.join(self.pid_dir, f"{server_id}.pid")
    
    def _write_pid_file(self, server_id: str, pid: int) -> None:
        """
        Write a PID file for a server.
        
        Args:
            server_id: Server identifier.
            pid: Process ID.
        """
        with open(self._get_pid_file(server_id), 'w') as f:
            f.write(str(pid))
    
    def _read_pid_file(self, server_id: str) -> Optional[int]:
        """
        Read a PID file for a server.
        
        Args:
            server_id: Server identifier.
            
        Returns:
            Process ID, or None if the file doesn't exist.
        """
        pid_file = self._get_pid_file(server_id)
        if not os.path.exists(pid_file):
            return None
        
        try:
            with open(pid_file, 'r') as f:
                return int(f.read().strip())
        except (IOError, ValueError):
            return None
    
    def _remove_pid_file(self, server_id: str) -> None:
        """
        Remove a PID file for a server.
        
        Args:
            server_id: Server identifier.
        """
        pid_file = self._get_pid_file(server_id)
        if os.path.exists(pid_file):
            os.remove(pid_file)
    
    def _is_process_running(self, pid: int) -> bool:
        """
        Check if a process is running.
        
        Args:
            pid: Process ID.
            
        Returns:
            True if the process is running, False otherwise.
        """
        try:
            # Check if the process exists
            process = psutil.Process(pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
    
    def start_server(self, server_id: str, command: str, args: List[str] = None, 
                     env: Dict[str, str] = None, wait_time: int = 5) -> Tuple[bool, Optional[str]]:
        """
        Start an MCP server.
        
        Args:
            server_id: Server identifier.
            command: Command to start the server.
            args: Command arguments.
            env: Environment variables.
            wait_time: Time to wait for server to start (seconds).
            
        Returns:
            Tuple of (success, error_message).
        """
        # Check if the server is already running
        pid = self._read_pid_file(server_id)
        if pid and self._is_process_running(pid):
            return True, None  # Server is already running
        
        # Remove stale PID file if it exists
        self._remove_pid_file(server_id)
        
        try:
            # Set up the environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Start the server
            logger.info(f"Starting MCP server '{server_id}': {command} {' '.join(args or [])}")
            process = subprocess.Popen(
                [command] + (args or []),
                env=process_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store the process
            self.active_processes[server_id] = process
            
            # Write the PID file
            self._write_pid_file(server_id, process.pid)
            
            # Wait for the server to start
            start_time = time.time()
            while time.time() - start_time < wait_time:
                if not self._is_process_running(process.pid):
                    # Process has exited early, which likely indicates an error
                    stdout, stderr = process.communicate(timeout=1)
                    error_msg = f"Server failed to start: {stderr}"
                    logger.error(error_msg)
                    self._remove_pid_file(server_id)
                    return False, error_msg
                
                # Check if the process has output that we can read
                try:
                    stdout = ""
                    if process.stdout:
                        stdout = process.stdout.readline()
                    if "Server started" in stdout or "Listening" in stdout:
                        logger.info(f"MCP server '{server_id}' started successfully")
                        return True, None
                except Exception:
                    pass
                
                time.sleep(0.1)
            
            # We've waited long enough, assume the server is running
            logger.info(f"MCP server '{server_id}' start timeout exceeded, assuming it's running")
            return True, None
            
        except Exception as e:
            error_msg = f"Error starting server: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def stop_server(self, server_id: str, force: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Stop an MCP server.
        
        Args:
            server_id: Server identifier.
            force: Whether to forcefully terminate the process.
            
        Returns:
            Tuple of (success, error_message).
        """
        # Check if we have an active process for this server
        if server_id in self.active_processes:
            process = self.active_processes[server_id]
            try:
                if force:
                    process.kill()
                else:
                    process.terminate()
                
                # Wait for the process to exit
                process.wait(timeout=5)
                
                # Remove the process from active processes
                del self.active_processes[server_id]
                self._remove_pid_file(server_id)
                
                logger.info(f"MCP server '{server_id}' stopped successfully")
                return True, None
            
            except subprocess.TimeoutExpired:
                # Force kill if terminate times out
                process.kill()
                process.wait()
                del self.active_processes[server_id]
                self._remove_pid_file(server_id)
                
                logger.warning(f"MCP server '{server_id}' had to be forcefully terminated")
                return True, "Server had to be forcefully terminated"
            
            except Exception as e:
                error_msg = f"Error stopping server: {str(e)}"
                logger.error(error_msg)
                return False, error_msg
        
        # Check if we have a PID file for this server
        pid = self._read_pid_file(server_id)
        if pid:
            try:
                # Try to terminate the process
                if self._is_process_running(pid):
                    if force:
                        os.kill(pid, signal.SIGKILL)
                    else:
                        os.kill(pid, signal.SIGTERM)
                    
                    # Wait briefly to see if the process exits
                    time.sleep(2)
                    
                    # Check if the process is still running
                    if self._is_process_running(pid):
                        # Force kill the process
                        os.kill(pid, signal.SIGKILL)
                        time.sleep(1)
                
                # Remove the PID file
                self._remove_pid_file(server_id)
                
                logger.info(f"MCP server '{server_id}' stopped successfully using PID file")
                return True, None
            
            except ProcessLookupError:
                # Process already gone, just remove the PID file
                self._remove_pid_file(server_id)
                logger.info(f"MCP server '{server_id}' was already stopped")
                return True, None
            
            except Exception as e:
                error_msg = f"Error stopping server: {str(e)}"
                logger.error(error_msg)
                return False, error_msg
        
        # No process or PID file found
        logger.warning(f"No running MCP server found for '{server_id}'")
        return False, "No running server found"
    
    def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """
        Get the status of an MCP server.
        
        Args:
            server_id: Server identifier.
            
        Returns:
            Dictionary with status information.
        """
        result = {
            "server_id": server_id,
            "running": False,
            "pid": None,
            "uptime": None,
            "memory_usage": None
        }
        
        # Check active processes first
        if server_id in self.active_processes:
            process = self.active_processes[server_id]
            result["pid"] = process.pid
            
            try:
                # Get process information using psutil
                p = psutil.Process(process.pid)
                result["running"] = p.is_running()
                result["uptime"] = time.time() - p.create_time()
                result["memory_usage"] = p.memory_info().rss / (1024 * 1024)  # MB
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process has disappeared or can't be accessed
                del self.active_processes[server_id]
                self._remove_pid_file(server_id)
                return result
            
            return result
        
        # Check PID file
        pid = self._read_pid_file(server_id)
        if pid:
            result["pid"] = pid
            
            try:
                # Get process information using psutil
                p = psutil.Process(pid)
                result["running"] = p.is_running()
                result["uptime"] = time.time() - p.create_time()
                result["memory_usage"] = p.memory_info().rss / (1024 * 1024)  # MB
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process has disappeared or can't be accessed
                self._remove_pid_file(server_id)
            
            return result
        
        return result
    
    def get_all_servers_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all MCP servers.
        
        Returns:
            Dictionary mapping server IDs to status dictionaries.
        """
        # Get all PID files
        servers = {}
        pid_files = [f for f in os.listdir(self.pid_dir) if f.endswith('.pid')]
        
        for pid_file in pid_files:
            server_id = pid_file[:-4]  # Remove .pid extension
            servers[server_id] = self.get_server_status(server_id)
        
        # Add any active processes that don't have PID files
        for server_id in self.active_processes:
            if server_id not in servers:
                servers[server_id] = self.get_server_status(server_id)
        
        return servers


# Example usage
if __name__ == "__main__":
    lifecycle = MCPServerLifecycle()
    
    # List all running servers
    servers = lifecycle.get_all_servers_status()
    print(f"Found {len(servers)} running servers:")
    for server_id, status in servers.items():
        running = "RUNNING" if status["running"] else "STOPPED"
        pid = status["pid"] or "N/A"
        uptime = f"{status['uptime']:.2f}s" if status["uptime"] else "N/A"
        print(f"  - {server_id}: {running} (PID: {pid}, Uptime: {uptime})")
