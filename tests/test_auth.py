"""Tests for authentication endpoints."""

import pytest


@pytest.mark.asyncio
async def test_register_new_user(client):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "newpass123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user):
    """Test registering with existing email."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "testuser@example.com", "password": "testpass123"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    """Test successful login."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with non-existent email."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "anypass"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client, user_token):
    """Test getting current user info."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client):
    """Test getting user info without auth."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403
