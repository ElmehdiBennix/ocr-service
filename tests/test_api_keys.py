"""Tests for API key endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_api_key(client, user_token):
    """Test creating an API key."""
    response = await client.post(
        "/api/v1/keys/create",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Test Key", "rate_limit": 100}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Key"
    assert data["rate_limit"] == 100
    assert "api_key" in data  # Plain key returned once
    assert data["api_key"].startswith("ocr_")


@pytest.mark.asyncio
async def test_create_api_key_unauthorized(client):
    """Test creating API key without auth."""
    response = await client.post(
        "/api/v1/keys/create",
        json={"name": "Test Key"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_api_keys(client, user_token):
    """Test listing user's API keys."""
    # Create a key first
    await client.post(
        "/api/v1/keys/create",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Test Key"}
    )
    
    response = await client.get(
        "/api/v1/keys/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "api_key" not in data[0]  # Hashed key not returned


@pytest.mark.asyncio
async def test_delete_api_key(client, user_token):
    """Test deleting an API key."""
    # Create a key first
    create_response = await client.post(
        "/api/v1/keys/create",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Test Key"}
    )
    key_id = create_response.json()["id"]
    
    # Delete it
    response = await client.delete(
        f"/api/v1/keys/{key_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    
    # Verify it's gone
    list_response = await client.get(
        "/api/v1/keys/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    keys = list_response.json()
    assert all(k["id"] != key_id for k in keys)
