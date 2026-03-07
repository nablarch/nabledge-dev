"""Logging configuration for knowledge-creator tool.

Provides unified logging infrastructure with both console and file output.
"""

import logging
import os
import sys
from typing import Optional


def setup_logger(log_file_path: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Configure and return the root logger for knowledge-creator.

    Args:
        log_file_path: Path to log file. If None, only console logging is enabled.
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger("knowledge_creator")

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    logger.setLevel(level)

    # Create formatters
    console_formatter = logging.Formatter(
        '%(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if path provided)
    if log_file_path:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


def get_logger() -> logging.Logger:
    """Get the knowledge-creator logger instance.

    Returns:
        Logger instance (auto-initializes if not yet configured)
    """
    logger = logging.getLogger("knowledge_creator")

    # Auto-initialize if not yet configured
    if not logger.handlers:
        setup_logger()

    return logger
