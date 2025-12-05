"""
CSRF protection middleware using Double Submit Cookie pattern.

Protects against Cross-Site Request Forgery attacks by:
- Generating CSRF tokens on GET requests
- Validating tokens on state-changing requests (POST, PUT, DELETE, PATCH)
- Using secure, httpOnly cookies
- Requiring X-CSRF-Token header validation
"""

import hashlib
import hmac
import os
import secrets
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.logging_config import get_logger

logger = get_logger(__name__)

# CSRF token configuration
CSRF_TOKEN_LENGTH = 32
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Methods that don't require CSRF protection
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect against CSRF attacks using Double Submit Cookie pattern.

    Features:
    - Generates CSRF token on GET requests
    - Validates token on state-changing requests
    - Uses secure, httpOnly cookies
    - Exempts safe methods (GET, HEAD, OPTIONS, TRACE)
    """

    def __init__(self, app, exempt_paths: list[str] | None = None):
        """
        Initialize CSRF middleware.

        Args:
            app: FastAPI application instance
            exempt_paths: List of paths to exempt from CSRF protection
        """
        super().__init__(app)
        self.exempt_paths = exempt_paths or []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and enforce CSRF protection.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response: Response with CSRF token header
        """
        # Skip CSRF check for safe methods
        if request.method in SAFE_METHODS:
            response = await call_next(request)
            # Generate and set CSRF token for GET requests
            if request.method == "GET":
                csrf_token = self._generate_csrf_token()
                response.headers[CSRF_HEADER_NAME] = csrf_token
                self._set_csrf_cookie(response, csrf_token)
            return response

        # Skip CSRF check for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Validate CSRF token for state-changing requests
        if not self._validate_csrf_token(request):
            logger.warning(
                "CSRF token validation failed",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "client_ip": request.client.host if request.client else "unknown",
                },
            )
            return JSONResponse(
                status_code=403,
                content={
                    "error_type": "SECURITY",
                    "message": "CSRF token validation failed",
                    "details": {"reason": "Invalid or missing CSRF token"},
                },
            )

        # Process request
        response = await call_next(request)

        # Refresh CSRF token in response
        csrf_token = self._generate_csrf_token()
        response.headers[CSRF_HEADER_NAME] = csrf_token
        self._set_csrf_cookie(response, csrf_token)

        return response

    def _generate_csrf_token(self) -> str:
        """
        Generate a new CSRF token.

        Returns:
            str: Hex-encoded CSRF token
        """
        token = secrets.token_hex(CSRF_TOKEN_LENGTH)
        return token

    def _validate_csrf_token(self, request: Request) -> bool:
        """
        Validate CSRF token from request.

        Compares token from header and cookie using constant-time comparison.

        Args:
            request: FastAPI request object

        Returns:
            bool: True if token is valid, False otherwise
        """
        # Get token from header
        header_token = request.headers.get(CSRF_HEADER_NAME)
        if not header_token:
            logger.debug("CSRF header missing", extra={"path": str(request.url.path)})
            return False

        # Get token from cookie
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        if not cookie_token:
            logger.debug("CSRF cookie missing", extra={"path": str(request.url.path)})
            return False

        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(header_token, cookie_token)

    def _set_csrf_cookie(self, response: Response, token: str) -> None:
        """
        Set CSRF token in secure cookie.

        Args:
            response: FastAPI response object
            token: CSRF token to set
        """
        is_production = os.getenv("APP_ENV") == "production"

        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=token,
            httponly=True,  # Prevent JavaScript access
            secure=is_production,  # HTTPS only in production
            samesite="strict",  # Prevent CSRF
            max_age=3600,  # 1 hour
        )
