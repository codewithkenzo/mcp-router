"""
File utilities for working with MCP server files.
Provides functions for reading, writing, and managing files related to MCP servers.
"""

import os
import json
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, TextIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_directory(path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory.
        
    Returns:
        Absolute path to the directory.
    """
    path = os.path.expanduser(path)
    os.makedirs(path, exist_ok=True)
    return path

def read_json_file(file_path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Read a JSON file.
    
    Args:
        file_path: Path to the JSON file.
        default: Default value to return if the file doesn't exist or can't be parsed.
        
    Returns:
        Parsed JSON data.
    """
    file_path = os.path.expanduser(file_path)
    
    if not os.path.exists(file_path):
        return default or {}
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        return default or {}

def write_json_file(file_path: str, data: Dict[str, Any], pretty: bool = True) -> bool:
    """
    Write data to a JSON file.
    
    Args:
        file_path: Path to the JSON file.
        data: Data to write.
        pretty: Whether to pretty-print the JSON.
        
    Returns:
        True if successful, False otherwise.
    """
    file_path = os.path.expanduser(file_path)
    
    try:
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(file_path, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
        
        return True
    except (IOError, TypeError) as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        return False

def atomic_write_json_file(file_path: str, data: Dict[str, Any], pretty: bool = True) -> bool:
    """
    Write data to a JSON file atomically.
    
    Args:
        file_path: Path to the JSON file.
        data: Data to write.
        pretty: Whether to pretty-print the JSON.
        
    Returns:
        True if successful, False otherwise.
    """
    file_path = os.path.expanduser(file_path)
    
    try:
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write to a temporary file first
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=parent_dir, suffix='.tmp') as temp_file:
            if pretty:
                json.dump(data, temp_file, indent=2)
            else:
                json.dump(data, temp_file)
        
        # Rename the temporary file to the target file
        shutil.move(temp_file.name, file_path)
        
        return True
    except (IOError, TypeError) as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        return False

def safe_delete_file(file_path: str) -> bool:
    """
    Safely delete a file.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        True if the file was deleted or doesn't exist, False on error.
    """
    file_path = os.path.expanduser(file_path)
    
    if not os.path.exists(file_path):
        return True
    
    try:
        os.remove(file_path)
        return True
    except IOError as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False

def find_first_existing_file(file_paths: List[str], default: Optional[str] = None) -> Optional[str]:
    """
    Find the first existing file from a list of paths.
    
    Args:
        file_paths: List of file paths to check.
        default: Default value to return if none of the files exist.
        
    Returns:
        Path to the first existing file, or default if none exist.
    """
    for path in file_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            return expanded_path
    
    return default

def get_user_data_dir(app_name: str = "mcp-router") -> str:
    """
    Get the user data directory for the application.
    
    Args:
        app_name: Name of the application.
        
    Returns:
        Path to the user data directory.
    """
    home = os.path.expanduser("~")
    
    # Linux/Unix
    if os.name == "posix":
        # Use XDG_DATA_HOME if available, otherwise ~/.local/share
        data_home = os.environ.get("XDG_DATA_HOME")
        if data_home:
            base_dir = data_home
        else:
            base_dir = os.path.join(home, ".local/share")
    # Windows
    elif os.name == "nt":
        base_dir = os.environ.get("APPDATA", os.path.join(home, "AppData/Roaming"))
    # macOS
    elif os.name == "darwin":
        base_dir = os.path.join(home, "Library/Application Support")
    # Fallback
    else:
        base_dir = os.path.join(home, ".config")
    
    app_dir = os.path.join(base_dir, app_name)
    os.makedirs(app_dir, exist_ok=True)
    
    return app_dir

def get_user_config_dir(app_name: str = "mcp-router") -> str:
    """
    Get the user configuration directory for the application.
    
    Args:
        app_name: Name of the application.
        
    Returns:
        Path to the user configuration directory.
    """
    home = os.path.expanduser("~")
    
    # Linux/Unix
    if os.name == "posix":
        # Use XDG_CONFIG_HOME if available, otherwise ~/.config
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            base_dir = config_home
        else:
            base_dir = os.path.join(home, ".config")
    # Windows
    elif os.name == "nt":
        base_dir = os.environ.get("APPDATA", os.path.join(home, "AppData/Roaming"))
    # macOS
    elif os.name == "darwin":
        base_dir = os.path.join(home, "Library/Application Support")
    # Fallback
    else:
        base_dir = os.path.join(home, ".config")
    
    app_dir = os.path.join(base_dir, app_name)
    os.makedirs(app_dir, exist_ok=True)
    
    return app_dir

def list_files_with_extension(directory: str, extension: str) -> List[str]:
    """
    List all files in a directory with a specific extension.
    
    Args:
        directory: Directory to search.
        extension: File extension to match (with or without dot).
        
    Returns:
        List of matching file paths.
    """
    directory = os.path.expanduser(directory)
    
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return []
    
    # Ensure extension starts with a dot
    if not extension.startswith("."):
        extension = f".{extension}"
    
    matching_files = []
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            matching_files.append(os.path.join(directory, filename))
    
    return matching_files

def create_file_if_not_exists(file_path: str, default_content: str = "") -> bool:
    """
    Create a file if it doesn't exist.
    
    Args:
        file_path: Path to the file.
        default_content: Default content to write to the file.
        
    Returns:
        True if the file was created or already exists, False on error.
    """
    file_path = os.path.expanduser(file_path)
    
    if os.path.exists(file_path):
        return True
    
    try:
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(default_content)
        
        return True
    except IOError as e:
        logger.error(f"Error creating file {file_path}: {e}")
        return False

def backup_file(file_path: str, backup_suffix: str = ".bak") -> Optional[str]:
    """
    Create a backup of a file.
    
    Args:
        file_path: Path to the file to back up.
        backup_suffix: Suffix to add to the backup file name.
        
    Returns:
        Path to the backup file, or None if the backup failed.
    """
    file_path = os.path.expanduser(file_path)
    
    if not os.path.exists(file_path):
        return None
    
    backup_path = f"{file_path}{backup_suffix}"
    
    try:
        shutil.copy2(file_path, backup_path)
        return backup_path
    except IOError as e:
        logger.error(f"Error backing up file {file_path}: {e}")
        return None

def restore_backup(backup_path: str, original_path: Optional[str] = None) -> bool:
    """
    Restore a file from a backup.
    
    Args:
        backup_path: Path to the backup file.
        original_path: Path to restore to. If None, will strip backup suffix.
        
    Returns:
        True if the backup was restored, False otherwise.
    """
    backup_path = os.path.expanduser(backup_path)
    
    if not os.path.exists(backup_path):
        return False
    
    if original_path is None:
        # Attempt to derive original path by removing common backup suffixes
        for suffix in [".bak", ".backup", ".old", ".prev"]:
            if backup_path.endswith(suffix):
                original_path = backup_path[:-len(suffix)]
                break
        
        if original_path is None:
            logger.error(f"Could not determine original path for backup {backup_path}")
            return False
    
    original_path = os.path.expanduser(original_path)
    
    try:
        shutil.copy2(backup_path, original_path)
        return True
    except IOError as e:
        logger.error(f"Error restoring backup {backup_path} to {original_path}: {e}")
        return False
