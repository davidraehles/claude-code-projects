"""
Security middleware for FastAPI.

Implements HTTPS enforcement and security headers for production environments.
Includes HSTS, content security policies, and other browser security features.
"""

import os
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

# Configure logging
logger = logging.getLogger(__name__)

# Configuration from environment variables
ENFORCE_HTTPS = os.getenv("ENFORCE_HTTPS", "false").lower() == "true"
APP_ENV = os.getenv("APP_ENV", "development")
HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year default
HSTS_INCLUDE_SUBDOMAINS = os.getenv("HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true"
HSTS_PRELOAD = os.getenv("HSTS_PRELOAD", "false").lower() == "true"

# Security headers configuration
SECURITY_HEADERS = {
    # Prevent MIME type sniffing
    "X-Content-Type-Options": "nosniff",

    # Prevent clickjacking
    "X-Frame-Options": "DENY",

    # Enable XSS protection (legacy, but still useful for older browsers)
    "X-XSS-Protection": "1; mode=block",

    # Control referrer information
    "Referrer-Policy": "strict-origin-when-cross-origin",

    # Prevent browsers from opening downloads
    "X-Download-Options": "noopen",

    # Prevent content type sniffing in IE
    "X-Permitted-Cross-Domain-Policies": "none",
}

# Content Security Policy (configurable)
CSP_ENABLED = os.getenv("CSP_ENABLED", "false").lower() == "true"
CSP_POLICY = os.getenv(
    "CSP_POLICY",
    "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; "
    "font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS and add security headers.

    Features:
    - HTTPS redirect (production only)
    - HTTP Strict Transport Security (HSTS)
    - Various security headers (XSS, clickjacking, etc.)
    - Content Security Policy (optional)
    """

    def __init__(self, app):
        """
        Initialize security middleware.

        Args:
            app: FastAPI application
        """
        super().__init__(app)

        # Log configuration
        if ENFORCE_HTTPS:
            logger.info("HTTPS enforcement is ENABLED")
        else:
            logger.info("HTTPS enforcement is DISABLED (set ENFORCE_HTTPS=true to enable)")

        logger.info(f"Security headers: {list(SECURITY_HEADERS.keys())}")

        if CSP_ENABLED:
            logger.info("Content Security Policy is ENABLED")

    def should_redirect_to_https(self, request: Request) -> bool:
        """
        Determine if request should be redirected to HTTPS.

        Args:
            request: The incoming request

        Returns:
            True if should redirect, False otherwise
        """
        # Only enforce HTTPS if explicitly enabled and not in development
        if not ENFORCE_HTTPS or APP_ENV == "development":
            return False

        # Check if request is already HTTPS
        if request.url.scheme == "https":
            return False

        # Check for X-Forwarded-Proto header (common in reverse proxies)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
        if forwarded_proto == "https":
            return False

        # Check for other proxy headers
        if request.headers.get("X-Forwarded-Ssl") == "on":
            return False

        # Request is HTTP and should be redirected
        return True

    def build_hsts_header(self) -> str:
        """
        Build HTTP Strict Transport Security header value.

        Returns:
            HSTS header value
        """
        hsts_parts = [f"max-age={HSTS_MAX_AGE}"]

        if HSTS_INCLUDE_SUBDOMAINS:
            hsts_parts.append("includeSubDomains")

        if HSTS_PRELOAD:
            hsts_parts.append("preload")

        return "; ".join(hsts_parts)

    def add_security_headers(self, response):
        """
        Add security headers to response.

        Args:
            response: The HTTP response to modify
        """
        # Add standard security headers
        for header_name, header_value in SECURITY_HEADERS.items():
            response.headers[header_name] = header_value

        # Add HSTS header if HTTPS is being used
        # Note: HSTS should only be sent over HTTPS connections
        if ENFORCE_HTTPS and APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = self.build_hsts_header()

        # Add Content Security Policy if enabled
        if CSP_ENABLED:
            response.headers["Content-Security-Policy"] = CSP_POLICY

        # Add Permissions Policy (formerly Feature Policy)
        # Restricts access to browser features
        permissions_policy = os.getenv(
            "PERMISSIONS_POLICY",
            "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
            "magnetometer=(), gyroscope=(), accelerometer=()"
        )
        if permissions_policy:
            response.headers["Permissions-Policy"] = permissions_policy

    async def dispatch(self, request: Request, call_next):
        """
        Process request and add security headers.

        Args:
            request: The incoming request
            call_next: The next middleware/handler

        Returns:
            Response: The HTTP response with security headers
        """
        # Check if we should redirect to HTTPS
        if self.should_redirect_to_https(request):
            # Build HTTPS URL
            https_url = request.url.replace(scheme="https")

            # Log redirect
            logger.info(f"Redirecting HTTP to HTTPS: {request.url} -> {https_url}")

            # Return 301 permanent redirect
            return RedirectResponse(url=str(https_url), status_code=301)

        # Process request
        response = await call_next(request)

        # Add security headers to response
        self.add_security_headers(response)

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware that only adds security headers without HTTPS enforcement.

    Use this if you want security headers but handle HTTPS at a different layer
    (e.g., load balancer, reverse proxy).
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and add security headers.

        Args:
            request: The incoming request
            call_next: The next middleware/handler

        Returns:
            Response: The HTTP response with security headers
        """
        response = await call_next(request)

        # Add standard security headers
        for header_name, header_value in SECURITY_HEADERS.items():
            response.headers[header_name] = header_value

        # Add HSTS if in production and request is HTTPS
        if APP_ENV == "production":
            # Check if request is over HTTPS
            is_https = (
                request.url.scheme == "https" or
                request.headers.get("X-Forwarded-Proto") == "https" or
                request.headers.get("X-Forwarded-Ssl") == "on"
            )

            if is_https:
                hsts_parts = [f"max-age={HSTS_MAX_AGE}"]
                if HSTS_INCLUDE_SUBDOMAINS:
                    hsts_parts.append("includeSubDomains")
                if HSTS_PRELOAD:
                    hsts_parts.append("preload")
                response.headers["Strict-Transport-Security"] = "; ".join(hsts_parts)

        # Add CSP if enabled
        if CSP_ENABLED:
            response.headers["Content-Security-Policy"] = CSP_POLICY

        return response
