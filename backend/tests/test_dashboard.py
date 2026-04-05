"""Tests for Dashboard API endpoints."""

import pytest


@pytest.fixture
async def test_owner_user(client):
    """Create a test owner user."""
    response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": "dashboard_owner",
            "name": "Dashboard Owner",
            "role": "owner",
        },
    )
    return response.json()


@pytest.fixture
async def test_tenant_user(client):
    """Create a test tenant user."""
    response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": "dashboard_tenant",
            "name": "Dashboard Tenant",
            "role": "tenant",
        },
    )
    return response.json()


@pytest.fixture
async def test_house(client, test_owner_user):
    """Create a test house."""
    response = await client.post(
        "/api/v1/houses",
        json={
            "name": "Dashboard Test House",
            "description": "A house for dashboard tests",
            "capacity": 8,
            "is_active": True,
        },
    )
    return response.json()


@pytest.fixture
async def test_tariff(client):
    """Create a test tariff."""
    response = await client.post(
        "/api/v1/tariffs",
        json={
            "name": "Test Tariff",
            "amount": 100,
        },
    )
    return response.json()


@pytest.mark.asyncio
async def test_get_owner_dashboard(client):
    """Test getting owner dashboard."""
    response = await client.get("/api/v1/dashboard/owner")
    assert response.status_code == 200
    data = response.json()
    assert "total_bookings" in data
    assert "total_revenue" in data
    assert "occupancy_rate" in data
    assert "active_bookings" in data
    assert "monthly_revenue" in data


@pytest.mark.asyncio
async def test_get_leaderboard(client):
    """Test getting leaderboard."""
    response = await client.get("/api/v1/dashboard/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert "bookings_by_month" in data
    assert "revenue_by_house" in data


@pytest.mark.asyncio
async def test_get_house_stats(client, test_house):
    """Test getting house statistics."""
    response = await client.get(f"/api/v1/dashboard/houses/{test_house['id']}/stats")
    assert response.status_code == 200
    data = response.json()
    assert "occupancy_rate" in data
    assert "total_revenue" in data
    assert "total_bookings" in data


@pytest.mark.asyncio
async def test_get_house_stats_not_found(client):
    """Test getting stats for non-existent house."""
    response = await client.get("/api/v1/dashboard/houses/99999/stats")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_house_stats_with_period(client, test_house):
    """Test getting house statistics with different periods."""
    for period in ["30d", "90d", "1y"]:
        response = await client.get(
            f"/api/v1/dashboard/houses/{test_house['id']}/stats?period={period}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "occupancy_rate" in data
        assert "total_revenue" in data
        assert "total_bookings" in data


@pytest.mark.asyncio
async def test_dashboard_with_bookings(
    client, test_house, test_tenant_user, test_tariff
):
    """Test dashboard with actual booking data."""
    from datetime import date, timedelta

    # Create a booking
    check_in = (date.today() + timedelta(days=10)).isoformat()
    check_out = (date.today() + timedelta(days=15)).isoformat()

    booking_response = await client.post(
        "/api/v1/bookings",
        json={
            "house_id": test_house["id"],
            "check_in": check_in,
            "check_out": check_out,
            "guests": [{"tariff_id": test_tariff["id"], "count": 4}],
        },
    )
    assert booking_response.status_code == 201

    # Get dashboard - should reflect the booking
    response = await client.get("/api/v1/dashboard/owner")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bookings"] >= 1
    assert data["active_bookings"] >= 1

    # Get house stats
    stats_response = await client.get(
        f"/api/v1/dashboard/houses/{test_house['id']}/stats"
    )
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_bookings"] >= 1
