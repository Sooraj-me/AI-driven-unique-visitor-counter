import os
import sys
from loguru import logger

def setup_logger(log_dir, log_level="INFO", rotation="10 MB", retention="7 days"):
    """
    Setup comprehensive logging configuration
    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        rotation: Log file rotation size
        retention: Log file retention period
    """
    try:
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Remove default logger
        logger.remove()
        
        # Add console logger
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True
        )
        
        # Add file logger with rotation
        logger.add(
            os.path.join(log_dir, "events.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip"
        )
        
        # Add error logger
        logger.add(
            os.path.join(log_dir, "errors.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation=rotation,
            retention=retention,
            compression="zip"
        )
        
        logger.info(f"Logging configured - Level: {log_level}, Directory: {log_dir}")
        return logger
        
    except Exception as e:
        print(f"Error setting up logger: {e}")
        # Fallback to basic logging
        logger.add(sys.stdout, level="INFO")
        return logger

def get_logger():
    """
    Get the configured logger instance
    """
    return logger 