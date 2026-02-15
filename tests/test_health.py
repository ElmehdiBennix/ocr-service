"""Tests for health check endpoints."""

import pytest


@pytest.mark.asyncio
async def test_basic_health_check(client):
    """Test basic health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_detailed_health_check(client):
    """Test detailed health endpoint."""
    response = await client.get("/health/details")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    assert "version" in data
