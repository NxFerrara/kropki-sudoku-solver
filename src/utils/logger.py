"""
Logging configuration for the Kropki Sudoku solver.
"""
import logging
import sys
from typing import Dict

# ANSI color codes
COLORS: Dict[str, str] = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[32m',      # Green
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[41m',  # Red background
    'RESET': '\033[0m'       # Reset
}

class ColorFormatter(logging.Formatter):
    """Custom formatter that adds colors and consistent formatting."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        # Handle separator differently
        if getattr(record, 'separator', False):
            return ""
            
        # Get color for this level
        color = COLORS.get(record.levelname, '')
        reset = COLORS['RESET']
        
        # Color the level indicator
        level_indicator = f"{color}[{record.levelname}]{reset}"
        record.levelname = level_indicator
        
        # Color the message if it exists
        if record.msg:
            record.msg = f"{color}{str(record.msg).replace('\n', ' ')}{reset}"
        
        return super().format(record)

class SeparatorLogger(logging.Logger):
    """Custom logger with additional functionality."""
    
    def separator(self) -> None:
        """Log an empty line for visual separation."""
        record = logging.LogRecord(
            name=self.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="",
            args=(),
            exc_info=None
        )
        record.separator = True
        self.handle(record)

class ColorHandler(logging.StreamHandler):
    """Custom handler that properly handles None from formatter."""
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record."""
        try:
            msg = self.format(record)
            self.stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

def setup_logger(name: str, level: int = logging.INFO) -> SeparatorLogger:
    """
    Set up a logger with colored console output.
    
    Args:
        name: Logger name
        level: Initial logging level (default: INFO)
        
    Returns:
        SeparatorLogger: Configured logger with separator functionality
    """
    # Register our custom logger class
    logging.setLoggerClass(SeparatorLogger)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)  # Set initial level
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    console_formatter = ColorFormatter('%(levelname)s %(message)s')
    
    # Use our custom handler instead of StreamHandler
    console_handler = ColorHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger