"""
Centralized Logger Utility
Configures file and console logging for Onboarding Operations.
All system events, audit actions, database operations, and errors are written to app.log.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import BASE_DIR

LOG_FILE_PATH = BASE_DIR / "app.log"

def setup_logger(name: str = "OnboardingOps") -> logging.Logger:
    """Configures and returns a logger instance with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Human-readable log format: YYYY-MM-DD HH:MM:SS | LEVEL | LOGGER_NAME | MESSAGE
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler - Writes to app.log with UTF-8 encoding
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler - Stream output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Default application logger instance
app_logger = setup_logger("OnboardingOps")
