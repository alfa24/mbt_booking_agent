"""Tests for house API endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_repository():
    """Clear repository before each test."""
    from backend.services.house import get_house_repository
    from backend.services.booking import get_booking_repository

    house_repo = get_house_repository()
    booking_repo = get_booking_repository()
    house_repo.clear()
    booking_repo.clear()
    # Reset the singleton instances to ensure clean state
    get_house_repository._instance = house_repo
    get_booking_repository._instance = booking_repo
    yield


class TestCreateHouse:
    """Tests for POST /api/v1/houses"""

    def test_create_house_success(self):
        """Test creating a house with valid data."""
        response = client.post(
            "/api/v1/houses",
            json={
                "name": "Старый дом",
                "description": "Уютный дом у озера",
                "capacity": 6,
                "is_active": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Старый дом"
        assert data["description"] == "Уютный дом у озера"
        assert data["capacity"] == 6
        assert data["is_active"] is True
        assert data["owner_id"] == 1
        assert "created_at" in data

    def test_create_house_minimal_data(self):
        """Test creating a house with minimal required data."""
        response = client.post(
            "/api/v1/houses",
            json={
                "name": "Новый дом",
                "capacity": 4,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Новый дом"
        assert data["capacity"] == 4
        assert data["is_active"] is True  # default value
        assert data["description"] is None

    def test_create_house_invalid_capacity(self):
        """Test creating a house with invalid capacity."""
        response = client.post(
            "/api/v1/houses",
            json={
                "name": "Дом",
                "capacity": 0,  # invalid: must be >= 1
            },
        )
        assert response.status_code == 422

    def test_create_house_empty_name(self):
        """Test creating a house with empty name."""
        response = client.post(
            "/api/v1/houses",
            json={
                "name": "",  # invalid: must be at least 1 char
                "capacity": 4,
            },
        )
        assert response.status_code == 422


class TestGetHouse:
    """Tests for GET /api/v1/houses/{id}"""

    def test_get_house_success(self):
        """Test getting an existing house."""
        # Create house first
        create_response = client.post(
            "/api/v1/houses",
            json={
                "name": "Тестовый дом",
                "capacity": 4,
            },
        )
        house_id = create_response.json()["id"]

        # Get the house
        response = client.get(f"/api/v1/houses/{house_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == house_id
        assert data["name"] == "Тестовый дом"

    def test_get_house_not_found(self):
        """Test getting a non-existent house."""
        response = client.get("/api/v1/houses/999")
        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestListHouses:
    """Tests for GET /api/v1/houses"""

    def test_list_houses_empty(self):
        """Test listing houses when none exist."""
        response = client.get("/api/v1/houses")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_houses_with_data(self):
        """Test listing multiple houses."""
        # Create two houses
        client.post(
            "/api/v1/houses",
            json={"name": "Дом 1", "capacity": 4},
        )
        client.post(
            "/api/v1/houses",
            json={"name": "Дом 2", "capacity": 6},
        )

        response = client.get("/api/v1/houses")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_houses_filter_by_owner(self):
        """Test filtering houses by owner_id."""
        # Create houses (all with owner_id=1 in MVP)
        client.post(
            "/api/v1/houses",
            json={"name": "Дом 1", "capacity": 4},
        )

        response = client.get("/api/v1/houses?owner_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

        response = client.get("/api/v1/houses?owner_id=999")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0

    def test_list_houses_filter_by_is_active(self):
        """Test filtering houses by is_active status."""
        # Create active house
        client.post(
            "/api/v1/houses",
            json={"name": "Активный дом", "capacity": 4, "is_active": True},
        )
        # Create inactive house
        client.post(
            "/api/v1/houses",
            json={"name": "Неактивный дом", "capacity": 6, "is_active": False},
        )

        response = client.get("/api/v1/houses?is_active=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Активный дом"

    def test_list_houses_filter_by_capacity(self):
        """Test filtering houses by capacity range."""
        # Create houses with different capacities
        client.post(
            "/api/v1/houses",
            json={"name": "Маленький", "capacity": 2},
        )
        client.post(
            "/api/v1/houses",
            json={"name": "Средний", "capacity": 4},
        )
        client.post(
            "/api/v1/houses",
            json={"name": "Большой", "capacity": 8},
        )

        # Filter by capacity_min
        response = client.get("/api/v1/houses?capacity_min=4")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

        # Filter by capacity_max
        response = client.get("/api/v1/houses?capacity_max=4")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

        # Filter by both
        response = client.get("/api/v1/houses?capacity_min=3&capacity_max=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Средний"

    def test_list_houses_pagination(self):
        """Test pagination with limit and offset."""
        # Create multiple houses
        for i in range(5):
            client.post(
                "/api/v1/houses",
                json={"name": f"Дом {i+1}", "capacity": 4},
            )

        response = client.get("/api/v1/houses?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1

    def test_list_houses_sorting(self):
        """Test sorting houses."""
        # Create houses
        client.post(
            "/api/v1/houses",
            json={"name": "Бета", "capacity": 4},
        )
        client.post(
            "/api/v1/houses",
            json={"name": "Альфа", "capacity": 6},
        )

        # Sort by name ascending
        response = client.get("/api/v1/houses?sort=name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Альфа"

        # Sort by name descending
        response = client.get("/api/v1/houses?sort=-name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Бета"


class TestUpdateHouse:
    """Tests for PATCH /api/v1/houses/{id}"""

    def test_update_house_partial(self):
        """Test partial update of house."""
        # Create house
        create_response = client.post(
            "/api/v1/houses",
            json={
                "name": "Старый дом",
                "description": "Описание",
                "capacity": 4,
                "is_active": True,
            },
        )
        house_id = create_response.json()["id"]

        # Update only name
        response = client.patch(
            f"/api/v1/houses/{house_id}",
            json={"name": "Новое название"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новое название"
        assert data["description"] == "Описание"  # unchanged
        assert data["capacity"] == 4  # unchanged

    def test_update_house_capacity(self):
        """Test updating house capacity."""
        # Create house
        create_response = client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = create_response.json()["id"]

        # Update capacity
        response = client.patch(
            f"/api/v1/houses/{house_id}",
            json={"capacity": 8},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] == 8

    def test_update_house_not_found(self):
        """Test updating a non-existent house."""
        response = client.patch(
            "/api/v1/houses/999",
            json={"name": "Новое название"},
        )
        assert response.status_code == 404

    def test_update_house_invalid_capacity(self):
        """Test updating with invalid capacity."""
        # Create house
        create_response = client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = create_response.json()["id"]

        # Try to update with invalid capacity
        response = client.patch(
            f"/api/v1/houses/{house_id}",
            json={"capacity": 0},
        )
        assert response.status_code == 422


class TestReplaceHouse:
    """Tests for PUT /api/v1/houses/{id}"""

    def test_replace_house_success(self):
        """Test full replacement of house."""
        # Create house
        create_response = client.post(
            "/api/v1/houses",
            json={
                "name": "Старый дом",
                "description": "Старое описание",
                "capacity": 4,
                "is_active": True,
            },
        )
        house_id = create_response.json()["id"]

        # Replace all fields
        response = client.put(
            f"/api/v1/houses/{house_id}",
            json={
                "name": "Новый дом",
                "description": "Новое описание",
                "capacity": 8,
                "is_active": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новый дом"
        assert data["description"] == "Новое описание"
        assert data["capacity"] == 8
        assert data["is_active"] is False

    def test_replace_house_not_found(self):
        """Test replacing a non-existent house."""
        response = client.put(
            "/api/v1/houses/999",
            json={
                "name": "Дом",
                "capacity": 4,
            },
        )
        assert response.status_code == 404


class TestDeleteHouse:
    """Tests for DELETE /api/v1/houses/{id}"""

    def test_delete_house_success(self):
        """Test deleting a house."""
        # Create house
        create_response = client.post(
            "/api/v1/houses",
            json={"name": "Дом для удаления", "capacity": 4},
        )
        house_id = create_response.json()["id"]

        # Delete house
        response = client.delete(f"/api/v1/houses/{house_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/v1/houses/{house_id}")
        assert get_response.status_code == 404

    def test_delete_house_not_found(self):
        """Test deleting a non-existent house."""
        response = client.delete("/api/v1/houses/999")
        assert response.status_code == 404


class TestGetHouseCalendar:
    """Tests for GET /api/v1/houses/{id}/calendar"""

    def test_get_calendar_empty(self):
        """Test getting calendar for house with no bookings."""
        # Create house
        create_response = client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = create_response.json()["id"]

        # Get calendar
        response = client.get(f"/api/v1/houses/{house_id}/calendar")
        assert response.status_code == 200
        data = response.json()
        assert data["house_id"] == house_id
        assert data["occupied_dates"] == []

    def test_get_calendar_with_bookings(self):
        """Test getting calendar with bookings."""
        # Create house
        house_response = client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = house_response.json()["id"]

        # Create booking for this house
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )

        # Get calendar
        response = client.get(f"/api/v1/houses/{house_id}/calendar")
        assert response.status_code == 200
        data = response.json()
        assert data["house_id"] == house_id
        assert len(data["occupied_dates"]) == 1
        assert data["occupied_dates"][0]["check_in"] == "2024-06-01"
        assert data["occupied_dates"][0]["check_out"] == "2024-06-05"
        assert "booking_id" in data["occupied_dates"][0]

    def test_get_calendar_house_not_found(self):
        """Test getting calendar for non-existent house."""
        response = client.get("/api/v1/houses/999/calendar")
        assert response.status_code == 404

    def test_get_calendar_cancelled_bookings_excluded(self):
        """Test that cancelled bookings don't appear in calendar."""
        # Create house
        house_response = client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = house_response.json()["id"]

        # Create and cancel booking
        booking_response = client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = booking_response.json()["id"]
        client.delete(f"/api/v1/bookings/{booking_id}")

        # Get calendar
        response = client.get(f"/api/v1/houses/{house_id}/calendar")
        assert response.status_code == 200
        data = response.json()
        assert data["occupied_dates"] == []

    def test_get_calendar_with_date_filter(self):
        """Test getting calendar with date range filter."""
        # Create house
        house_response = client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = house_response.json()["id"]

        # Create bookings in different periods
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-07-10",
                "check_out": "2024-07-15",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )

        # Get calendar with date filter
        response = client.get(
            f"/api/v1/houses/{house_id}/calendar?date_from=2024-06-01&date_to=2024-06-30"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["occupied_dates"]) == 1
        assert data["occupied_dates"][0]["check_in"] == "2024-06-01"
