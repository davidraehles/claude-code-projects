"""
Configuration and fixtures for smoke tests.

Smoke tests run against deployed environments to validate basic functionality.
"""

import os
from typing import Generator

import httpx
import pytest


@pytest.fixture(scope="module")
def base_url() -> str:
    """
    Get the base URL for the deployed environment.

    Returns:
        str: Base URL for API (from environment or default)
    """
    return os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="module")
def client(base_url: str) -> Generator[httpx.Client, None, None]:
    """
    Create an HTTP client for smoke tests.

    Args:
        base_url: Base URL for the API

    Yields:
        httpx.Client: Configured HTTP client
    """
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="module")
def async_client(base_url: str) -> Generator[httpx.AsyncClient, None, None]:
    """
    Create an async HTTP client for smoke tests.

    Args:
        base_url: Base URL for the API

    Yields:
        httpx.AsyncClient: Configured async HTTP client
    """
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="module")
def test_user_credentials() -> dict:
    """
    Get test user credentials for authentication tests.

    Returns:
        dict: Test user credentials
    """
    return {
        "email": os.getenv("SMOKE_TEST_EMAIL", "smoketest@example.com"),
        "password": os.getenv("SMOKE_TEST_PASSWORD", "SmokeTest123!"),
        "country": "US",
    }
