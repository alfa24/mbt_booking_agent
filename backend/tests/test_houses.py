"""Tests for house API endpoints."""

import pytest


class TestCreateHouse:
    """Tests for POST /api/v1/houses"""

    @pytest.mark.asyncio
    async def test_create_house_success(self, client):
        """Test creating a house with valid data."""
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_create_house_minimal_data(self, client):
        """Test creating a house with minimal required data."""
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_create_house_invalid_capacity(self, client):
        """Test creating a house with invalid capacity."""
        response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Дом",
                "capacity": 0,  # invalid: must be >= 1
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_house_empty_name(self, client):
        """Test creating a house with empty name."""
        response = await client.post(
            "/api/v1/houses",
            json={
                "name": "",  # invalid: must be at least 1 char
                "capacity": 4,
            },
        )
        assert response.status_code == 422


class TestGetHouse:
    """Tests for GET /api/v1/houses/{id}"""

    @pytest.mark.asyncio
    async def test_get_house_success(self, client):
        """Test getting an existing house."""
        # Create house first
        create_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Тестовый дом",
                "capacity": 4,
            },
        )
        house_id = create_response.json()["id"]

        # Get the house
        response = await client.get(f"/api/v1/houses/{house_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == house_id
        assert data["name"] == "Тестовый дом"

    @pytest.mark.asyncio
    async def test_get_house_not_found(self, client):
        """Test getting a non-existent house."""
        response = await client.get("/api/v1/houses/999")
        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestListHouses:
    """Tests for GET /api/v1/houses"""

    @pytest.mark.asyncio
    async def test_list_houses_empty(self, client):
        """Test listing houses when none exist."""
        response = await client.get("/api/v1/houses")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_houses_with_data(self, client):
        """Test listing multiple houses."""
        # Create two houses
        await client.post(
            "/api/v1/houses",
            json={"name": "Дом 1", "capacity": 4},
        )
        await client.post(
            "/api/v1/houses",
            json={"name": "Дом 2", "capacity": 6},
        )

        response = await client.get("/api/v1/houses")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_houses_filter_by_owner(self, client):
        """Test filtering houses by owner_id."""
        # Create houses (all with owner_id=1 in MVP)
        await client.post(
            "/api/v1/houses",
            json={"name": "Дом 1", "capacity": 4},
        )

        response = await client.get("/api/v1/houses?owner_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

        response = await client.get("/api/v1/houses?owner_id=999")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0

    @pytest.mark.asyncio
    async def test_list_houses_filter_by_is_active(self, client):
        """Test filtering houses by is_active status."""
        # Create active house
        await client.post(
            "/api/v1/houses",
            json={"name": "Активный дом", "capacity": 4, "is_active": True},
        )
        # Create inactive house
        await client.post(
            "/api/v1/houses",
            json={"name": "Неактивный дом", "capacity": 6, "is_active": False},
        )

        response = await client.get("/api/v1/houses?is_active=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Активный дом"

    @pytest.mark.asyncio
    async def test_list_houses_filter_by_capacity(self, client):
        """Test filtering houses by capacity range."""
        # Create houses with different capacities
        await client.post(
            "/api/v1/houses",
            json={"name": "Маленький", "capacity": 2},
        )
        await client.post(
            "/api/v1/houses",
            json={"name": "Средний", "capacity": 4},
        )
        await client.post(
            "/api/v1/houses",
            json={"name": "Большой", "capacity": 8},
        )

        # Filter by capacity_min
        response = await client.get("/api/v1/houses?capacity_min=4")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

        # Filter by capacity_max
        response = await client.get("/api/v1/houses?capacity_max=4")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

        # Filter by both
        response = await client.get("/api/v1/houses?capacity_min=3&capacity_max=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Средний"

    @pytest.mark.asyncio
    async def test_list_houses_pagination(self, client):
        """Test pagination with limit and offset."""
        # Create multiple houses
        for i in range(5):
            await client.post(
                "/api/v1/houses",
                json={"name": f"Дом {i+1}", "capacity": 4},
            )

        response = await client.get("/api/v1/houses?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1

    @pytest.mark.asyncio
    async def test_list_houses_sorting(self, client):
        """Test sorting houses."""
        # Create houses
        await client.post(
            "/api/v1/houses",
            json={"name": "Бета", "capacity": 4},
        )
        await client.post(
            "/api/v1/houses",
            json={"name": "Альфа", "capacity": 6},
        )

        # Sort by name ascending
        response = await client.get("/api/v1/houses?sort=name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Альфа"

        # Sort by name descending
        response = await client.get("/api/v1/houses?sort=-name")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Бета"


class TestUpdateHouse:
    """Tests for PATCH /api/v1/houses/{id}"""

    @pytest.mark.asyncio
    async def test_update_house_partial(self, client):
        """Test partial update of house."""
        # Create house
        create_response = await client.post(
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
        response = await client.patch(
            f"/api/v1/houses/{house_id}",
            json={"name": "Новое название"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новое название"
        assert data["description"] == "Описание"  # unchanged
        assert data["capacity"] == 4  # unchanged

    @pytest.mark.asyncio
    async def test_update_house_capacity(self, client):
        """Test updating house capacity."""
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = create_response.json()["id"]

        # Update capacity
        response = await client.patch(
            f"/api/v1/houses/{house_id}",
            json={"capacity": 8},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] == 8

    @pytest.mark.asyncio
    async def test_update_house_not_found(self, client):
        """Test updating a non-existent house."""
        response = await client.patch(
            "/api/v1/houses/999",
            json={"name": "Новое название"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_house_invalid_capacity(self, client):
        """Test updating with invalid capacity."""
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = create_response.json()["id"]

        # Try to update with invalid capacity
        response = await client.patch(
            f"/api/v1/houses/{house_id}",
            json={"capacity": 0},
        )
        assert response.status_code == 422


class TestReplaceHouse:
    """Tests for PUT /api/v1/houses/{id}"""

    @pytest.mark.asyncio
    async def test_replace_house_success(self, client):
        """Test full replacement of house."""
        # Create house
        create_response = await client.post(
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
        response = await client.put(
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

    @pytest.mark.asyncio
    async def test_replace_house_not_found(self, client):
        """Test replacing a non-existent house."""
        response = await client.put(
            "/api/v1/houses/999",
            json={
                "name": "Дом",
                "capacity": 4,
            },
        )
        assert response.status_code == 404


class TestDeleteHouse:
    """Tests for DELETE /api/v1/houses/{id}"""

    @pytest.mark.asyncio
    async def test_delete_house_success(self, client):
        """Test deleting a house."""
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом для удаления", "capacity": 4},
        )
        house_id = create_response.json()["id"]

        # Delete house
        response = await client.delete(f"/api/v1/houses/{house_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(f"/api/v1/houses/{house_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_house_not_found(self, client):
        """Test deleting a non-existent house."""
        response = await client.delete("/api/v1/houses/999")
        assert response.status_code == 404


class TestGetHouseCalendar:
    """Tests for GET /api/v1/houses/{id}/calendar"""

    @pytest.mark.asyncio
    async def test_get_calendar_empty(self, client):
        """Test getting calendar for house with no bookings."""
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = create_response.json()["id"]

        # Get calendar
        response = await client.get(f"/api/v1/houses/{house_id}/calendar")
        assert response.status_code == 200
        data = response.json()
        assert data["house_id"] == house_id
        assert data["occupied_dates"] == []

    @pytest.mark.asyncio
    async def test_get_calendar_with_bookings(self, client):
        """Test getting calendar with bookings."""
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = house_response.json()["id"]

        # Create booking for this house
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )

        # Get calendar
        response = await client.get(f"/api/v1/houses/{house_id}/calendar")
        assert response.status_code == 200
        data = response.json()
        assert data["house_id"] == house_id
        assert len(data["occupied_dates"]) == 1
        assert data["occupied_dates"][0]["check_in"] == "2024-06-01"
        assert data["occupied_dates"][0]["check_out"] == "2024-06-05"
        assert "booking_id" in data["occupied_dates"][0]

    @pytest.mark.asyncio
    async def test_get_calendar_house_not_found(self, client):
        """Test getting calendar for non-existent house."""
        response = await client.get("/api/v1/houses/999/calendar")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_calendar_cancelled_bookings_excluded(self, client):
        """Test that cancelled bookings don't appear in calendar."""
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = house_response.json()["id"]

        # Create and cancel booking
        booking_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        booking_id = booking_response.json()["id"]
        await client.delete(f"/api/v1/bookings/{booking_id}")

        # Get calendar
        response = await client.get(f"/api/v1/houses/{house_id}/calendar")
        assert response.status_code == 200
        data = response.json()
        assert data["occupied_dates"] == []

    @pytest.mark.asyncio
    async def test_get_calendar_with_date_filter(self, client):
        """Test getting calendar with date range filter."""
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4},
        )
        house_id = house_response.json()["id"]

        # Create bookings in different periods
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-07-10",
                "check_out": "2024-07-15",
                "guests": [{"tariff_id": 2, "count": 2}],
            },
        )

        # Get calendar with date filter
        response = await client.get(
            f"/api/v1/houses/{house_id}/calendar?date_from=2024-06-01&date_to=2024-06-30"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["occupied_dates"]) == 1
        assert data["occupied_dates"][0]["check_in"] == "2024-06-01"
