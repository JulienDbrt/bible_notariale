import sys
from pathlib import Path
from loguru import logger
from typing import Optional, Any

# Remove default logger
logger.remove()

# Add console handler with custom format
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Add file handler for errors
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="1 week",
    backtrace=True,
    diagnose=True,
)

# Add file handler for all logs
logger.add(
    log_dir / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="100 MB",
    retention="3 days",
    backtrace=False,
    diagnose=False,
)

def get_logger(name: Optional[str] = None) -> Any:
    """Get a logger instance with optional name binding"""
    if name:
        return logger.bind(name=name)
    return logger

# Export configured logger
__all__ = ["logger", "get_logger"]