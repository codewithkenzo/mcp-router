"""
Tests for the logger module in the MCP adapter.
"""

import unittest
import os
import logging
import tempfile
from pathlib import Path
from src.core.logger import MCPLogger

class TestMCPLogger(unittest.TestCase):
    """Test the MCPLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary file for log output
        self.temp_log_file = tempfile.NamedTemporaryFile(delete=False)
        self.log_path = Path(self.temp_log_file.name)
        self.temp_log_file.close()

    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary log file
        if os.path.exists(self.log_path):
            os.unlink(self.log_path)

    def test_logger_initialization(self):
        """Test logger initialization."""
        # First, clear any existing handlers to get a clean slate
        logging.getLogger("test").handlers = []
        
        logger = MCPLogger(name="test", debug_mode=True, log_file=self.log_path)
        
        # Check that logger is named correctly
        self.assertEqual(logger.logger.name, "test")
        
        # Check that log file was created
        self.assertTrue(os.path.exists(self.log_path))
        
        # Handler count varies, so just check that we have at least one handler
        self.assertGreaterEqual(len(logger.logger.handlers), 1)
        
        # Should be at DEBUG level when debug=True
        self.assertEqual(logger.logger.level, logging.DEBUG)

    def test_logger_with_debug_false(self):
        """Test logger initialization with debug=False."""
        logger = MCPLogger(name="test", debug_mode=False, log_file=self.log_path)
        
        # Should be at INFO level when debug=False
        self.assertEqual(logger.logger.level, logging.INFO)

    def test_log_levels(self):
        """Test different log levels."""
        logger = MCPLogger(name="test", debug_mode=True, log_file=self.log_path)
        
        # Test various log levels
        logger.log_debug("Debug message")
        logger.log_info("Info message")
        logger.log_warning("Warning message")
        logger.log_error("Error message")
        
        # Check file contents
        with open(self.log_path, 'r') as file:
            log_content = file.read()
            
        self.assertIn("DEBUG", log_content)
        self.assertIn("INFO", log_content)
        self.assertIn("WARNING", log_content)
        self.assertIn("ERROR", log_content)
        self.assertIn("Debug message", log_content)
        self.assertIn("Info message", log_content)
        self.assertIn("Warning message", log_content)
        self.assertIn("Error message", log_content)

    def test_session_tracking(self):
        """Test session start and end tracking."""
        logger = MCPLogger(name="test", debug_mode=True, log_file=self.log_path)
        
        # Start session is already called in __init__
        # End the session
        logger.end_session(status="completed")
        
        with open(self.log_path, 'r') as file:
            log_content = file.read()
            
        self.assertIn("Session started at", log_content)
        self.assertIn("Session completed at", log_content)
        self.assertIn("completed", log_content)

    def test_session_failure(self):
        """Test session failure status."""
        logger = MCPLogger(name="test", debug_mode=True, log_file=self.log_path)
        
        # End the session with failed status
        logger.end_session(status="failed")
        
        with open(self.log_path, 'r') as file:
            log_content = file.read()
            
        self.assertIn("Session failed at", log_content)

    def test_no_file_logger(self):
        """Test logger without a log file."""
        # First, clear any existing handlers to get a clean slate
        logging.getLogger("test").handlers = []
        
        logger = MCPLogger(name="test", debug_mode=True, log_file=None)
        
        # Should have at least one handler (console)
        self.assertGreaterEqual(len(logger.logger.handlers), 1)
        
        # Can log without errors
        logger.log_info("Test message")
        logger.end_session("completed")

    def test_logger_formatter(self):
        """Test logger formatter."""
        logger = MCPLogger(name="custom_name", debug_mode=True, log_file=self.log_path)
        logger.log_info("Test formatter")
        
        with open(self.log_path, 'r') as file:
            log_content = file.read()
            
        # Check that name is included in log format
        self.assertIn("[custom_name]", log_content)

if __name__ == "__main__":
    unittest.main()