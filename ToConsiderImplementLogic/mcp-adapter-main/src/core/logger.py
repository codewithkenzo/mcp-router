import logging
from typing import Optional
from pathlib import Path
from datetime import datetime

class MCPLogger:
    """Logger class for MCP Adapter SDK components"""
    
    def __init__(self, 
                 name: str, 
                 debug_mode: bool = False, 
                 log_file: Optional[Path] = None):
        self.logger = logging.getLogger(name)
        self.debug_mode = debug_mode
        self.start_time = datetime.now()
        
        # Set base level based on debug mode
        base_level = logging.DEBUG if debug_mode else logging.INFO
        self.logger.setLevel(base_level)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
        )
        console_formatter = logging.Formatter(
            '[%(name)s][%(levelname)s] %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(base_level)
        self.logger.addHandler(console_handler)
        
        # File handler (if log_file specified)
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            self.logger.addHandler(file_handler)
            
        # Log session start
        self.log_info("=" * 50)
        self.log_info(f"Session started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_info("-" * 50)
    
    def log_debug(self, msg: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(msg, *args, **kwargs)
    
    def log_info(self, msg: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(msg, *args, **kwargs)
    
    def log_warning(self, msg: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(msg, *args, **kwargs)
    
    def log_error(self, msg: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(msg, *args, **kwargs)
        
    def end_session(self, status: str = "completed"):
        """Log session end with duration"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self.log_info("-" * 50)
        self.log_info(f"Session {status} at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_info(f"Duration: {duration}")
        self.log_info("=" * 50 + "\n")