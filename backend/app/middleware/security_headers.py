"""
Security Headers Middleware for FastAPI.

Adds security-related HTTP headers to all responses to protect against
common web vulnerabilities and attacks:

- X-Content-Type-Options: Prevent MIME type sniffing
- X-Frame-Options: Prevent clickjacking attacks
- X-XSS-Protection: Enable browser XSS protection
- Content-Security-Policy: Define content sources
- Strict-Transport-Security: Enforce HTTPS
- Referrer-Policy: Control referrer information
- Permissions-Policy: Control browser features

These headers improve security posture and help achieve compliance
with security standards and best practices.
"""

import os
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.

    Headers are configured based on environment and security requirements.
    Production environments enforce stricter policies.
    """

    def __init__(self, app, enable_hsts: bool = True, hsts_max_age: int = 31536000):
        """
        Initialize security headers middleware.

        Args:
            app: FastAPI application instance
            enable_hsts: Whether to enable HSTS (should be True in production)
            hsts_max_age: HSTS max-age in seconds (default: 1 year)
        """
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.is_production = os.getenv("APP_ENV", "development") == "production"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response: Response with security headers added
        """
        # Process the request
        response = await call_next(request)

        # Add security headers to response
        self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response) -> None:
        """
        Add all security headers to the response.

        Args:
            response: FastAPI response object to modify
        """
        # X-Content-Type-Options: Prevent MIME sniffing
        # Ensures browsers respect declared content types
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        # Prevents the page from being embedded in frames/iframes
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Enable browser XSS filtering
        # Legacy header but still provides protection for older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content-Security-Policy: Define allowed content sources
        # Mitigates XSS and other injection attacks
        csp_policy = self._build_csp_policy()
        response.headers["Content-Security-Policy"] = csp_policy

        # Strict-Transport-Security: Enforce HTTPS
        # Only add in production or if explicitly enabled
        if self.enable_hsts:
            hsts_value = f"max-age={self.hsts_max_age}; includeSubDomains"
            if self.is_production:
                # Add preload in production for maximum security
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

        # Referrer-Policy: Control referrer information leakage
        # Balances privacy and functionality
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Control browser features
        # Restricts access to sensitive APIs and hardware
        response.headers["Permissions-Policy"] = self._build_permissions_policy()

    def _build_csp_policy(self) -> str:
        """
        Build Content Security Policy based on environment.

        Returns:
            CSP policy string
        """
        if self.is_production:
            # Strict policy for production
            return (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "  # Allow inline styles for UI frameworks
                "img-src 'self' data: https:; "  # Allow images from HTTPS sources
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "  # Prevent framing (redundant with X-Frame-Options)
                "base-uri 'self'; "
                "form-action 'self'; "
                "upgrade-insecure-requests"  # Upgrade HTTP to HTTPS
            )
        else:
            # More relaxed policy for development
            return (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' ws: wss:; "  # Allow WebSocket for dev tools
                "frame-ancestors 'none'"
            )

    def _build_permissions_policy(self) -> str:
        """
        Build Permissions Policy (formerly Feature-Policy).

        Restricts access to browser features and APIs.

        Returns:
            Permissions policy string
        """
        # Deny most permissions by default
        # Only enable what's explicitly needed
        return (
            "camera=(), "  # No camera access
            "microphone=(), "  # No microphone access
            "geolocation=(), "  # No geolocation
            "payment=(), "  # No payment API
            "usb=(), "  # No USB access
            "magnetometer=(), "  # No magnetometer
            "gyroscope=(), "  # No gyroscope
            "accelerometer=(), "  # No accelerometer
            "interest-cohort=()"  # Disable FLoC tracking
        )
