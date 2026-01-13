"""
Logging Configuration
=====================

Centralized logging setup using Loguru with rich formatting.

Usage:
    from entrainer_selection.core.logging import setup_logging, get_logger
    
    setup_logging()  # Call once at application startup
    logger = get_logger(__name__)
    logger.info("Processing started")
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def setup_logging(
    level: str = "INFO",
    log_format: Optional[str] = None,
    log_directory: str = "./logs",
    rotation: str = "10 MB",
    retention: str = "1 week",
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string (uses Loguru format)
        log_directory: Directory for log files
        rotation: When to rotate log files (e.g., "10 MB", "1 day")
        retention: How long to keep old log files
    """
    # Remove default handler
    logger.remove()
    
    # Default format with rich context
    if log_format is None:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
    
    # Console handler with colors
    logger.add(
        sys.stderr,
        format=log_format,
        level=level,
        colorize=True,
    )
    
    # Ensure log directory exists
    log_path = Path(log_directory)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # File handler for all logs
    logger.add(
        log_path / "entrainer_{time:YYYY-MM-DD}.log",
        format=log_format.replace("<green>", "").replace("</green>", "")
              .replace("<level>", "").replace("</level>", "")
              .replace("<cyan>", "").replace("</cyan>", ""),
        level=level,
        rotation=rotation,
        retention=retention,
        compression="zip",
    )
    
    # Separate error log
    logger.add(
        log_path / "errors_{time:YYYY-MM-DD}.log",
        format=log_format.replace("<green>", "").replace("</green>", "")
              .replace("<level>", "").replace("</level>", "")
              .replace("<cyan>", "").replace("</cyan>", ""),
        level="ERROR",
        rotation=rotation,
        retention=retention,
        compression="zip",
    )
    
    logger.info(f"Logging initialized at {level} level")


def get_logger(name: str):
    """
    Get a logger instance bound to a specific module name.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance with module context
    """
    return logger.bind(name=name)


# Phase-specific loggers for easy filtering
def get_phase_logger(phase: str):
    """
    Get a logger for a specific phase.
    
    Args:
        phase: Phase identifier (e.g., "phase_1", "phase_2a")
        
    Returns:
        Logger instance with phase context
    """
    return logger.bind(phase=phase)

