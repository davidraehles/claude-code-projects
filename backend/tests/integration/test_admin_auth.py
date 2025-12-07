"""Integration tests for admin authentication on protected endpoints.

Tests for PR #42 security fix: Admin authentication on rate limit API endpoints.
"""

from datetime import datetime

import pytest
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import create_access_token, create_refresh_token
from app.models.user import User
from app.database import AsyncSessionLocal


@pytest.fixture
async def admin_user(db: AsyncSession):
    """Create an admin user for testing."""
    user = User(
        email="admin@test.com",
        password_hash="hashed_password",
        country="US",
        is_admin=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def non_admin_user(db: AsyncSession):
    """Create a non-admin user for testing."""
    user = User(
        email="user@test.com",
        password_hash="hashed_password",
        country="US",
        is_admin=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_admin_rate_limit_list_policies_requires_admin(client, non_admin_user):
    """Test that listing rate limit policies requires admin privileges."""
    # Create token for non-admin user
    token = create_access_token({"sub": str(non_admin_user.id)})

    response = client.get(
        "/admin/rate-limits/policies",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Admin privileges required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_admin_rate_limit_list_policies_allows_admin(client, admin_user):
    """Test that listing rate limit policies works for admin users."""
    # Create token for admin user
    token = create_access_token({"sub": str(admin_user.id)})

    response = client.get(
        "/admin/rate-limits/policies",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_admin_rate_limit_endpoints_require_auth(client):
    """Test that admin rate limit endpoints require authentication."""
    endpoints = [
        ("GET", "/admin/rate-limits/policies"),
        ("POST", "/admin/rate-limits/policies"),
        ("GET", "/admin/rate-limits/overrides"),
        ("POST", "/admin/rate-limits/overrides"),
        ("GET", "/admin/rate-limits/whitelist"),
        ("POST", "/admin/rate-limits/whitelist"),
        ("POST", "/admin/rate-limits/clear-cache"),
        ("POST", "/admin/rate-limits/seed-defaults"),
    ]

    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})

        # Should fail with 403 Forbidden (missing Authorization header)
        # or 422 Unprocessable Entity (invalid request body)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.asyncio
async def test_admin_rate_limit_create_policy_admin_only(client, non_admin_user, admin_user):
    """Test that creating rate limit policies requires admin privileges."""
    non_admin_token = create_access_token({"sub": str(non_admin_user.id)})
    admin_token = create_access_token({"sub": str(admin_user.id)})

    policy_data = {
        "endpoint_pattern": "^/api/v1/test$",
        "limit_type": "per_ip",
        "requests_per_window": 10,
        "window_seconds": 60,
    }

    # Non-admin should be denied
    response = client.post(
        "/admin/rate-limits/policies",
        json=policy_data,
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Admin should be allowed
    response = client.post(
        "/admin/rate-limits/policies",
        json=policy_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # Status might be 201 (created) or 400+ if validation fails, but not 403
    assert response.status_code != status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_admin_whitelist_endpoints_require_admin(client, non_admin_user):
    """Test that whitelist management requires admin privileges."""
    token = create_access_token({"sub": str(non_admin_user.id)})

    response = client.get(
        "/admin/rate-limits/whitelist",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Admin privileges required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_deleted_user_cannot_be_admin(client, db: AsyncSession):
    """Test that deleted users cannot access admin endpoints even if is_admin=True."""
    # Create deleted admin user
    user = User(
        email="deleted_admin@test.com",
        password_hash="hashed_password",
        country="US",
        is_admin=True,
        deleted_at=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    response = client.get(
        "/admin/rate-limits/policies",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]
