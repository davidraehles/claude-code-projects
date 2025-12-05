"""
Structured logging configuration with JSON formatting.

Provides centralized logging setup with:
- JSON formatting via python-json-logger
- Request ID injection for distributed tracing
- Configurable log levels via environment
- Separate loggers for app, uvicorn.access, uvicorn.error
"""

import logging
import os
import sys
from contextvars import ContextVar
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

# Context variable for request ID (thread-safe)
request_id_context: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """
    Logging filter that adds request_id to log records.

    Uses contextvars for thread-safe request ID storage.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add request_id to the log record.

        Args:
            record: Log record to modify

        Returns:
            bool: Always True (don't filter out records)
        """
        record.request_id = request_id_context.get() or "N/A"
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with additional fields.

    Adds service metadata and formats exceptions properly.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """
        Add custom fields to the JSON log record.

        Args:
            log_record: JSON log record to modify
            record: Original log record
            message_dict: Additional message fields
        """
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record["timestamp"] = self.formatTime(record, self.datefmt)

        # Add log level
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add service metadata
        log_record["service"] = "recipe-meal-planning-api"
        log_record["environment"] = os.getenv("APP_ENV", "production")

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add request ID if present
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Sets up:
    - JSON formatters for all loggers
    - Request ID filters
    - Log level from LOG_LEVEL environment variable
    - Handlers for stdout
    """
    # Get log level from environment (default: INFO)
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Create JSON formatter
    json_formatter = CustomJsonFormatter(
        fmt="%(timestamp)s %(level)s %(logger)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    # Create request ID filter
    request_id_filter = RequestIdFilter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    stdout_handler.setFormatter(json_formatter)
    stdout_handler.addFilter(request_id_filter)
    root_logger.addHandler(stdout_handler)

    # Configure app logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    app_logger.propagate = True  # Propagate to root logger

    # Configure uvicorn access logger
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(log_level)
    uvicorn_access_logger.handlers = []

    access_handler = logging.StreamHandler(sys.stdout)
    access_handler.setLevel(log_level)
    access_handler.setFormatter(json_formatter)
    access_handler.addFilter(request_id_filter)
    uvicorn_access_logger.addHandler(access_handler)
    uvicorn_access_logger.propagate = False

    # Configure uvicorn error logger
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.setLevel(log_level)
    uvicorn_error_logger.handlers = []

    error_handler = logging.StreamHandler(sys.stdout)
    error_handler.setLevel(log_level)
    error_handler.setFormatter(json_formatter)
    error_handler.addFilter(request_id_filter)
    uvicorn_error_logger.addHandler(error_handler)
    uvicorn_error_logger.propagate = False

    # Log startup message
    app_logger.info(
        "Logging configured successfully",
        extra={
            "log_level": log_level_str,
            "environment": os.getenv("APP_ENV", "production"),
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """
    Set the request ID for the current context.

    Args:
        request_id: Unique request identifier
    """
    request_id_context.set(request_id)


def clear_request_id() -> None:
    """Clear the request ID from the current context."""
    request_id_context.set(None)


def get_request_id() -> Optional[str]:
    """
    Get the current request ID.

    Returns:
        Optional[str]: Current request ID or None
    """
    return request_id_context.get()
