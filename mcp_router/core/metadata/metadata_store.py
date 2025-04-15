"""
Metadata Store Module

This module provides a persistent storage system for MCP server metadata,
allowing for efficient storage and retrieval of server information.
"""

import os
import json
import sqlite3
import logging
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class MetadataStore:
    """
    Persistent storage for MCP server metadata.
    
    This class provides a SQLite-based storage system for MCP server metadata,
    allowing for efficient storage and retrieval of server information.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the metadata store.
        
        Args:
            db_path: Optional path to the SQLite database file
        """
        self.db_path = db_path or os.path.expanduser("~/.mcp_router/metadata.db")
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Create servers table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                server_type TEXT NOT NULL,
                command TEXT NOT NULL,
                args TEXT NOT NULL,
                env TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create capabilities table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create server_capabilities table (many-to-many relationship)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS server_capabilities (
                server_id TEXT,
                capability_id INTEGER,
                PRIMARY KEY (server_id, capability_id),
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
                FOREIGN KEY (capability_id) REFERENCES capabilities(id) ON DELETE CASCADE
            )
            """)
            
            # Create tools table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                schema TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
                UNIQUE (server_id, name)
            )
            """)
            
            # Create server_health table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS server_health (
                server_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_check TIMESTAMP NOT NULL,
                last_successful_connection TIMESTAMP,
                error_count INTEGER DEFAULT 0,
                average_response_time REAL DEFAULT 0.0,
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
            )
            """)
            
            # Create server_usage table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS server_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                execution_time REAL NOT NULL,
                success BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
            )
            """)
            
            # Create server_tags table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS server_tags (
                server_id TEXT,
                tag TEXT,
                PRIMARY KEY (server_id, tag),
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
            )
            """)
            
            # Create indices for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_server_capabilities_server_id ON server_capabilities(server_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_server_capabilities_capability_id ON server_capabilities(capability_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tools_server_id ON tools(server_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_server_usage_server_id ON server_usage(server_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_server_usage_timestamp ON server_usage(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_server_tags_server_id ON server_tags(server_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_server_tags_tag ON server_tags(tag)")
    
    def store_server_metadata(self, server_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Store metadata about an MCP server.
        
        Args:
            server_id: Unique identifier for the server
            metadata: Dictionary containing server metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Convert args and env to JSON strings
                args_json = json.dumps(metadata.get('args', []))
                env_json = json.dumps(metadata.get('env', {}))
                
                # Insert or update server record
                conn.execute("""
                INSERT INTO servers (id, name, description, server_type, command, args, env, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    server_type = excluded.server_type,
                    command = excluded.command,
                    args = excluded.args,
                    env = excluded.env,
                    updated_at = CURRENT_TIMESTAMP
                """, (
                    server_id,
                    metadata.get('name', server_id),
                    metadata.get('description', ''),
                    metadata.get('server_type', 'unknown'),
                    metadata.get('command', ''),
                    args_json,
                    env_json
                ))
                
                # Store capabilities
                if 'capabilities' in metadata and isinstance(metadata['capabilities'], list):
                    for capability in metadata['capabilities']:
                        # Insert capability if it doesn't exist
                        conn.execute("""
                        INSERT OR IGNORE INTO capabilities (name, description)
                        VALUES (?, ?)
                        """, (capability, ''))
                        
                        # Get capability ID
                        cursor = conn.execute("SELECT id FROM capabilities WHERE name = ?", (capability,))
                        capability_id = cursor.fetchone()[0]
                        
                        # Link server to capability
                        conn.execute("""
                        INSERT OR IGNORE INTO server_capabilities (server_id, capability_id)
                        VALUES (?, ?)
                        """, (server_id, capability_id))
                
                # Store tools
                if 'tools' in metadata and isinstance(metadata['tools'], list):
                    for tool in metadata['tools']:
                        tool_name = tool.get('name', '')
                        tool_description = tool.get('description', '')
                        tool_schema = json.dumps(tool.get('schema', {}))
                        
                        conn.execute("""
                        INSERT INTO tools (server_id, name, description, schema, updated_at)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(server_id, name) DO UPDATE SET
                            description = excluded.description,
                            schema = excluded.schema,
                            updated_at = CURRENT_TIMESTAMP
                        """, (server_id, tool_name, tool_description, tool_schema))
                
                # Store tags
                if 'tags' in metadata and isinstance(metadata['tags'], list):
                    # First delete existing tags
                    conn.execute("DELETE FROM server_tags WHERE server_id = ?", (server_id,))
                    
                    # Then insert new tags
                    for tag in metadata['tags']:
                        conn.execute("""
                        INSERT INTO server_tags (server_id, tag)
                        VALUES (?, ?)
                        """, (server_id, tag))
                
                # Initialize health record if it doesn't exist
                conn.execute("""
                INSERT OR IGNORE INTO server_health (server_id, status, last_check)
                VALUES (?, 'unknown', CURRENT_TIMESTAMP)
                """, (server_id,))
                
            logger.info(f"Stored metadata for server: {server_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing server metadata: {e}")
            return False
    
    def get_server_metadata(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a specific server.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            Dictionary containing server metadata or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get server record
                cursor = conn.execute("SELECT * FROM servers WHERE id = ?", (server_id,))
                server_row = cursor.fetchone()
                
                if not server_row:
                    return None
                
                # Convert to dictionary
                server_data = dict(server_row)
                
                # Parse JSON fields
                server_data['args'] = json.loads(server_data['args'])
                server_data['env'] = json.loads(server_data['env'])
                
                # Get capabilities
                cursor = conn.execute("""
                SELECT c.name
                FROM capabilities c
                JOIN server_capabilities sc ON c.id = sc.capability_id
                WHERE sc.server_id = ?
                """, (server_id,))
                server_data['capabilities'] = [row[0] for row in cursor.fetchall()]
                
                # Get tools
                cursor = conn.execute("SELECT id, name, description, schema FROM tools WHERE server_id = ?", (server_id,))
                tools = []
                for row in cursor.fetchall():
                    tool_data = dict(row)
                    tool_data['schema'] = json.loads(tool_data['schema'])
                    tools.append(tool_data)
                server_data['tools'] = tools
                
                # Get health
                cursor = conn.execute("SELECT * FROM server_health WHERE server_id = ?", (server_id,))
                health_row = cursor.fetchone()
                if health_row:
                    server_data['health'] = dict(health_row)
                
                # Get tags
                cursor = conn.execute("SELECT tag FROM server_tags WHERE server_id = ?", (server_id,))
                server_data['tags'] = [row[0] for row in cursor.fetchall()]
                
                return server_data
        except Exception as e:
            logger.error(f"Error retrieving server metadata: {e}")
            return None
    
    def get_servers_for_task(self, task_description: str) -> List[str]:
        """
        Find servers that can handle a specific task based on stored metadata.
        
        Args:
            task_description: Description of the task
            
        Returns:
            List of server IDs that can handle the task
        """
        try:
            # Extract keywords from task description
            # This is a simple implementation; in a real system, you might use NLP
            keywords = [word.lower() for word in task_description.split() if len(word) > 3]
            
            if not keywords:
                return []
            
            with sqlite3.connect(self.db_path) as conn:
                # Build query to find servers with matching capabilities or tool descriptions
                placeholders = ', '.join(['?'] * len(keywords))
                like_clauses = ' OR '.join([f"c.name LIKE '%' || ? || '%'"] * len(keywords))
                tool_like_clauses = ' OR '.join([f"t.description LIKE '%' || ? || '%'"] * len(keywords))
                
                query = f"""
                SELECT DISTINCT s.id
                FROM servers s
                LEFT JOIN server_capabilities sc ON s.id = sc.server_id
                LEFT JOIN capabilities c ON sc.capability_id = c.id
                LEFT JOIN tools t ON s.id = t.server_id
                LEFT JOIN server_health sh ON s.id = sh.server_id
                WHERE (({like_clauses}) OR ({tool_like_clauses}))
                AND (sh.status = 'online' OR sh.status IS NULL)
                """
                
                # Double the keywords for both capability and tool description clauses
                params = keywords + keywords
                
                cursor = conn.execute(query, params)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error finding servers for task: {e}")
            return []
    
    def update_server_health(self, server_id: str, status: str, response_time: Optional[float] = None) -> bool:
        """
        Update the health status of a server.
        
        Args:
            server_id: Unique identifier for the server
            status: New status ("online", "offline", "error")
            response_time: Optional response time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                now = datetime.now().isoformat()
                
                # Check if server exists
                cursor = conn.execute("SELECT 1 FROM servers WHERE id = ?", (server_id,))
                if not cursor.fetchone():
                    logger.warning(f"Attempted to update health for unknown server: {server_id}")
                    return False
                
                # Get current health record
                cursor = conn.execute("SELECT * FROM server_health WHERE server_id = ?", (server_id,))
                health_row = cursor.fetchone()
                
                if health_row:
                    # Update existing record
                    if status == "online":
                        if response_time is not None:
                            # Update average response time with exponential moving average
                            alpha = 0.3  # Weight for new value
                            old_avg = health_row[5] if health_row[5] is not None else 0.0
                            new_avg = (alpha * response_time) + ((1 - alpha) * old_avg)
                            
                            conn.execute("""
                            UPDATE server_health
                            SET status = ?, last_check = ?, last_successful_connection = ?,
                                error_count = 0, average_response_time = ?
                            WHERE server_id = ?
                            """, (status, now, now, new_avg, server_id))
                        else:
                            conn.execute("""
                            UPDATE server_health
                            SET status = ?, last_check = ?, last_successful_connection = ?,
                                error_count = 0
                            WHERE server_id = ?
                            """, (status, now, now, server_id))
                    else:
                        # Increment error count for non-online status
                        error_count = health_row[4] + 1 if health_row[4] is not None else 1
                        conn.execute("""
                        UPDATE server_health
                        SET status = ?, last_check = ?, error_count = ?
                        WHERE server_id = ?
                        """, (status, now, error_count, server_id))
                else:
                    # Create new record
                    conn.execute("""
                    INSERT INTO server_health (server_id, status, last_check, last_successful_connection, 
                                              error_count, average_response_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        server_id,
                        status,
                        now,
                        now if status == "online" else None,
                        0 if status == "online" else 1,
                        response_time or 0.0
                    ))
                
                logger.info(f"Updated health for server: {server_id} to {status}")
                return True
        except Exception as e:
            logger.error(f"Error updating server health: {e}")
            return False
    
    def record_server_usage(self, server_id: str, tool_name: str, execution_time: float, success: bool) -> bool:
        """
        Record usage statistics for a server.
        
        Args:
            server_id: Unique identifier for the server
            tool_name: Name of the tool that was used
            execution_time: Time taken to execute the tool in seconds
            success: Whether the tool execution was successful
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                INSERT INTO server_usage (server_id, tool_name, execution_time, success)
                VALUES (?, ?, ?, ?)
                """, (server_id, tool_name, execution_time, success))
                
                logger.info(f"Recorded usage for server: {server_id}, tool: {tool_name}")
                return True
        except Exception as e:
            logger.error(f"Error recording server usage: {e}")
            return False
    
    def get_server_usage_stats(self, server_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get usage statistics for a server.
        
        Args:
            server_id: Unique identifier for the server
            days: Number of days to include in the statistics
            
        Returns:
            Dictionary containing usage statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Calculate timestamp for N days ago
                timestamp = datetime.now().timestamp() - (days * 86400)
                date_str = datetime.fromtimestamp(timestamp).isoformat()
                
                # Get total usage count
                cursor = conn.execute("""
                SELECT COUNT(*) as total_count,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                       AVG(execution_time) as avg_execution_time
                FROM server_usage
                WHERE server_id = ? AND timestamp >= ?
                """, (server_id, date_str))
                
                stats_row = cursor.fetchone()
                if not stats_row or stats_row[0] == 0:
                    return {
                        "total_count": 0,
                        "success_count": 0,
                        "failure_count": 0,
                        "success_rate": 0.0,
                        "avg_execution_time": 0.0,
                        "tools": []
                    }
                
                total_count = stats_row[0]
                success_count = stats_row[1] or 0
                avg_execution_time = stats_row[2] or 0.0
                
                # Get tool-specific statistics
                cursor = conn.execute("""
                SELECT tool_name,
                       COUNT(*) as count,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                       AVG(execution_time) as avg_execution_time
                FROM server_usage
                WHERE server_id = ? AND timestamp >= ?
                GROUP BY tool_name
                ORDER BY count DESC
                """, (server_id, date_str))
                
                tools = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "total_count": total_count,
                    "success_count": success_count,
                    "failure_count": total_count - success_count,
                    "success_rate": success_count / total_count if total_count > 0 else 0.0,
                    "avg_execution_time": avg_execution_time,
                    "tools": tools
                }
        except Exception as e:
            logger.error(f"Error getting server usage stats: {e}")
            return {
                "total_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "tools": [],
                "error": str(e)
            }
    
    def get_servers_by_tag(self, tag: str) -> List[str]:
        """
        Get servers with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of server IDs with the specified tag
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                SELECT server_id
                FROM server_tags
                WHERE tag = ?
                """, (tag,))
                
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting servers by tag: {e}")
            return []
    
    def get_servers_by_capability(self, capability: str) -> List[str]:
        """
        Get servers with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of server IDs with the specified capability
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                SELECT s.id
                FROM servers s
                JOIN server_capabilities sc ON s.id = sc.server_id
                JOIN capabilities c ON sc.capability_id = c.id
                WHERE c.name = ?
                """, (capability,))
                
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting servers by capability: {e}")
            return []
    
    def get_all_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get all capabilities in the system.
        
        Returns:
            List of dictionaries containing capability information
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                SELECT id, name, description, created_at,
                       (SELECT COUNT(*) FROM server_capabilities WHERE capability_id = capabilities.id) as server_count
                FROM capabilities
                ORDER BY server_count DESC, name
                """)
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all capabilities: {e}")
            return []
    
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """
        Get all tags in the system.
        
        Returns:
            List of dictionaries containing tag information
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                SELECT tag, COUNT(*) as server_count
                FROM server_tags
                GROUP BY tag
                ORDER BY server_count DESC, tag
                """)
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all tags: {e}")
            return []
    
    def delete_server(self, server_id: str) -> bool:
        """
        Delete a server and all its associated data.
        
        Args:
            server_id: Unique identifier for the server
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if server exists
                cursor = conn.execute("SELECT 1 FROM servers WHERE id = ?", (server_id,))
                if not cursor.fetchone():
                    logger.warning(f"Attempted to delete unknown server: {server_id}")
                    return False
                
                # Delete server (cascading deletes will handle related records)
                conn.execute("DELETE FROM servers WHERE id = ?", (server_id,))
                
                logger.info(f"Deleted server: {server_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting server: {e}")
            return False
