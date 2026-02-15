"""Tests for admin endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_users_as_admin(client, admin_token):
    """Test listing all users as admin."""
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_list_users_as_regular_user(client, user_token):
    """Test that regular users can't access admin endpoints."""
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_system_stats(client, admin_token):
    """Test getting system statistics."""
    response = await client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_api_keys" in data
