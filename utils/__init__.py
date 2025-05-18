# Utils package initialization
import logging
import os
import sys
from typing import Optional

# Set up default logger
logger = logging.getLogger("diligentizer")

class _NoTraceFormatter(logging.Formatter):
    """Formatter that never appends traceback lines."""
    def format(self, record):
        saved_exc = record.exc_info        # keep ref
        record.exc_info = None             # hide traceback
        try:
            return super().format(record)  # normal formatting
        finally:
            record.exc_info = saved_exc    # restore for other handlers (if any)

def configure_logger(
    log_level: str = "INFO", 
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure the diligentizer logger with the specified log level and outputs.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to a log file
        console_output: Whether to output logs to the console
        
    Returns:
        The configured logger
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Set the log level
    logger.setLevel(numeric_level)
    
    # Define log format
    formatter = _NoTraceFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add file handler if log_file is specified
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

# Configure the default logger with INFO level and console output
configure_logger()
