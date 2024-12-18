"""
Manual test script to demonstrate basic functionality.
Run this script directly to see logging output with different configurations.
"""
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger

def demonstrate_logging():
    """Demonstrate different logging configurations."""
    print("\n1. Testing all log levels:")
    print("-" * 50)
    logger = setup_logger("test", level=logging.DEBUG)
    
    # Test all log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    # Test separator
    logger.separator()
    
    # Test multiline message
    logger.info("This is a multiline\nmessage that should\nbe on one line")
    
    # Test empty message
    logger.info("")
    
    # Test message with special characters
    logger.warning("Special chars: !@#$%^&*()")

if __name__ == "__main__":
    demonstrate_logging()