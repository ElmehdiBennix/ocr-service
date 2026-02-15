"""Tests for user management endpoints."""

import pytest


@pytest.mark.asyncio
async def test_update_user_profile(client, user_token):
    """Test updating user profile."""
    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"quota_limit": 5000}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quota_limit"] == 5000


@pytest.mark.asyncio
async def test_update_user_unauthorized(client):
    """Test updating profile without auth."""
    response = await client.put(
        "/api/v1/users/me",
        json={"quota_limit": 5000}
    )
    assert response.status_code == 403
