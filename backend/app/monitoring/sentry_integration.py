"""
Sentry error tracking integration for FastAPI.

Provides centralized error tracking and monitoring:
- SDK initialization with environment-specific configuration
- Sensitive data filtering (passwords, tokens, PII)
- User context tracking
- Release version tracking
- Integration with structured logging
"""

import logging
import os
import subprocess
from typing import Any, Dict, Optional

from app.logging_config import get_logger

logger = get_logger(__name__)

# Sentry SDK is optional - only import if available
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.warning("Sentry SDK not installed - error tracking disabled")


# Sensitive field patterns to filter
SENSITIVE_FIELDS = {
    "password",
    "token",
    "secret",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "cookie",
    "csrf",
    "session",
    "private_key",
    "access_token",
    "refresh_token",
}


def before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter sensitive data before sending events to Sentry.

    Scrubs passwords, tokens, API keys, and other sensitive information
    from request data, headers, and exception context.

    Args:
        event: Sentry event dictionary
        hint: Additional context hints

    Returns:
        Modified event dictionary or None to drop the event
    """
    # Filter request data
    if "request" in event:
        request = event["request"]

        # Filter headers
        if "headers" in request:
            request["headers"] = _filter_dict(request["headers"])

        # Filter cookies
        if "cookies" in request:
            request["cookies"] = _filter_dict(request["cookies"])

        # Filter query string
        if "query_string" in request:
            request["query_string"] = "[Filtered]"

        # Filter request body
        if "data" in request:
            if isinstance(request["data"], dict):
                request["data"] = _filter_dict(request["data"])
            else:
                request["data"] = "[Filtered]"

    # Filter exception context
    if "exception" in event and "values" in event["exception"]:
        for exception in event["exception"]["values"]:
            if "stacktrace" in exception and "frames" in exception["stacktrace"]:
                for frame in exception["stacktrace"]["frames"]:
                    # Filter local variables
                    if "vars" in frame:
                        frame["vars"] = _filter_dict(frame["vars"])

    # Filter extra context
    if "extra" in event:
        event["extra"] = _filter_dict(event["extra"])

    return event


def _filter_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively filter sensitive fields from dictionary.

    Args:
        data: Dictionary to filter

    Returns:
        Filtered dictionary with sensitive values replaced
    """
    if not isinstance(data, dict):
        return data

    filtered = {}
    for key, value in data.items():
        # Check if key contains sensitive field name
        key_lower = str(key).lower()
        if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
            filtered[key] = "[Filtered]"
        elif isinstance(value, dict):
            filtered[key] = _filter_dict(value)
        elif isinstance(value, list):
            filtered[key] = [
                _filter_dict(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            filtered[key] = value

    return filtered


def get_git_release() -> Optional[str]:
    """
    Get current git commit SHA as release version.

    Returns:
        Git commit SHA or None if not available
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"Could not get git release version: {e}")

    return None


def init_sentry() -> None:
    """
    Initialize Sentry SDK for error tracking.

    Configuration from environment variables:
    - SENTRY_DSN: Sentry project DSN (required)
    - APP_ENV: Environment name (development/staging/production)
    - LOG_LEVEL: Minimum log level to capture

    Features:
    - FastAPI integration for request/response tracking
    - SQLAlchemy integration for database query tracking
    - Redis integration for cache operation tracking
    - Logging integration for error log capture
    - Sensitive data filtering
    - Release tracking from git
    """
    if not SENTRY_AVAILABLE:
        logger.info("Sentry SDK not available - skipping initialization")
        return

    # Get Sentry DSN from environment
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        logger.info("SENTRY_DSN not set - error tracking disabled")
        return

    # Get environment configuration
    environment = os.getenv("APP_ENV", "production")
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Get release version from git
    release = get_git_release()

    # Determine sample rate based on environment
    traces_sample_rate = 1.0 if environment == "development" else 0.1
    profiles_sample_rate = 1.0 if environment == "development" else 0.1

    try:
        # Initialize Sentry SDK
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(
                    level=log_level,  # Capture logs at this level and above
                    event_level=logging.ERROR,  # Create events for ERROR and above
                ),
            ],
            # Performance monitoring
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            # Privacy and filtering
            before_send=before_send,
            send_default_pii=False,  # Don't send PII automatically
            # Error handling
            max_breadcrumbs=50,
            attach_stacktrace=True,
            # Request data
            request_bodies="medium",  # Capture medium-sized request bodies
        )

        logger.info(
            "Sentry error tracking initialized",
            extra={
                "environment": environment,
                "release": release,
                "traces_sample_rate": traces_sample_rate,
            },
        )

    except Exception as e:
        logger.error(
            f"Failed to initialize Sentry: {e}",
            exc_info=True,
        )


def set_user_context(user_id: Optional[str], email: Optional[str] = None) -> None:
    """
    Set user context for Sentry events.

    Args:
        user_id: User ID to track
        email: Optional user email (will be filtered if PII protection enabled)
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        sentry_sdk.set_user({"id": user_id, "email": email})
    except Exception as e:
        logger.debug(f"Failed to set Sentry user context: {e}")


def clear_user_context() -> None:
    """Clear user context from Sentry events."""
    if not SENTRY_AVAILABLE:
        return

    try:
        sentry_sdk.set_user(None)
    except Exception as e:
        logger.debug(f"Failed to clear Sentry user context: {e}")


def capture_exception(error: Exception, **extra_context: Any) -> None:
    """
    Manually capture an exception to Sentry.

    Args:
        error: Exception to capture
        **extra_context: Additional context to attach
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        with sentry_sdk.push_scope() as scope:
            # Add extra context
            for key, value in extra_context.items():
                scope.set_extra(key, value)

            # Capture exception
            sentry_sdk.capture_exception(error)
    except Exception as e:
        logger.debug(f"Failed to capture exception to Sentry: {e}")


def capture_message(message: str, level: str = "info", **extra_context: Any) -> None:
    """
    Manually capture a message to Sentry.

    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        **extra_context: Additional context to attach
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        with sentry_sdk.push_scope() as scope:
            # Add extra context
            for key, value in extra_context.items():
                scope.set_extra(key, value)

            # Capture message
            sentry_sdk.capture_message(message, level=level)
    except Exception as e:
        logger.debug(f"Failed to capture message to Sentry: {e}")
