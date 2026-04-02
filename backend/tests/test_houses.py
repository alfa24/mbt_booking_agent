"""Tests for house API endpoints."""

import pytest


class TestCreateHouse:
    """Tests for POST /api/v1/houses"""

    @pytest.mark.asyncio
    async def test_create_house_success(self, client):
        """Test creating a house with valid data."""
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "house_test_user",
                "name": "House Test User",
                "role": "owner",
            },
        )
        assert user_response.status_code == 201
        user = user_response.json()
        
        response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Старый дом",
                "description": "Уютный дом у озера",
                "capacity": 6,
                "is_active": True,
                "owner_id": user["id"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Старый дом"
        assert data["description"] == "Уютный дом у озера"
        assert data["capacity"] == 6
        assert data["is_active"] is True
        assert data["owner_id"] == user["id"]
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_house_minimal_data(self, client):
        """Test creating a house with minimal required data."""
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "house_test_user2",
                "name": "House Test User 2",
                "role": "owner",
            },
        )
        assert user_response.status_code == 201
        user = user_response.json()
        
        response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Новый дом",
                "capacity": 4,
                "owner_id": user["id"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Новый дом"
        assert data["capacity"] == 4
        assert data["is_active"] is True  # default value
        assert data["description"] is None
        assert data["owner_id"] == user["id"]

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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "get_house_user",
                "name": "Get House User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house first
        create_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Тестовый дом",
                "capacity": 4,
                "owner_id": user["id"],
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "list_houses_user",
                "name": "List Houses User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create two houses
        await client.post(
            "/api/v1/houses",
            json={"name": "Дом 1", "capacity": 4, "owner_id": user["id"]},
        )
        await client.post(
            "/api/v1/houses",
            json={"name": "Дом 2", "capacity": 6, "owner_id": user["id"]},
        )

        response = await client.get("/api/v1/houses")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_houses_filter_by_owner(self, client):
        """Test filtering houses by owner_id."""
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "filter_owner_user",
                "name": "Filter Owner User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        await client.post(
            "/api/v1/houses",
            json={"name": "Дом 1", "capacity": 4, "owner_id": user["id"]},
        )

        response = await client.get(f"/api/v1/houses?owner_id={user['id']}")
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "filter_active_user",
                "name": "Filter Active User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create active house
        await client.post(
            "/api/v1/houses",
            json={"name": "Активный дом", "capacity": 4, "is_active": True, "owner_id": user["id"]},
        )
        # Create inactive house
        await client.post(
            "/api/v1/houses",
            json={"name": "Неактивный дом", "capacity": 6, "is_active": False, "owner_id": user["id"]},
        )

        response = await client.get("/api/v1/houses?is_active=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Активный дом"

    @pytest.mark.asyncio
    async def test_list_houses_filter_by_capacity(self, client):
        """Test filtering houses by capacity range."""
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "filter_capacity_user",
                "name": "Filter Capacity User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create houses with different capacities
        await client.post(
            "/api/v1/houses",
            json={"name": "Маленький", "capacity": 2, "owner_id": user["id"]},
        )
        await client.post(
            "/api/v1/houses",
            json={"name": "Средний", "capacity": 4, "owner_id": user["id"]},
        )
        await client.post(
            "/api/v1/houses",
            json={"name": "Большой", "capacity": 8, "owner_id": user["id"]},
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "pagination_user",
                "name": "Pagination User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create multiple houses
        for i in range(5):
            await client.post(
                "/api/v1/houses",
                json={"name": f"Дом {i+1}", "capacity": 4, "owner_id": user["id"]},
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "sorting_user",
                "name": "Sorting User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create houses
        await client.post(
            "/api/v1/houses",
            json={"name": "Бета", "capacity": 4, "owner_id": user["id"]},
        )
        await client.post(
            "/api/v1/houses",
            json={"name": "Альфа", "capacity": 6, "owner_id": user["id"]},
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "update_house_user",
                "name": "Update House User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Старый дом",
                "description": "Описание",
                "capacity": 4,
                "is_active": True,
                "owner_id": user["id"],
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "update_capacity_user",
                "name": "Update Capacity User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4, "owner_id": user["id"]},
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "update_invalid_user",
                "name": "Update Invalid User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4, "owner_id": user["id"]},
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "replace_house_user",
                "name": "Replace House User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Старый дом",
                "description": "Старое описание",
                "capacity": 4,
                "is_active": True,
                "owner_id": user["id"],
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "delete_house_user",
                "name": "Delete House User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом для удаления", "capacity": 4, "owner_id": user["id"]},
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "calendar_empty_user",
                "name": "Calendar Empty User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        create_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4, "owner_id": user["id"]},
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "calendar_booking_user",
                "name": "Calendar Booking User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4, "owner_id": user["id"]},
        )
        house_id = house_response.json()["id"]

        # Create tariff for booking
        tariff_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Adult", "amount": 250},
        )
        tariff_id = tariff_response.json()["id"]

        # Create booking for this house
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": tariff_id, "count": 2}],
            },
        )
        assert response.status_code == 201

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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "calendar_cancel_user",
                "name": "Calendar Cancel User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4, "owner_id": user["id"]},
        )
        house_id = house_response.json()["id"]

        # Create tariff for booking
        tariff_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Adult", "amount": 250},
        )
        tariff_id = tariff_response.json()["id"]

        # Create and cancel booking
        booking_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": tariff_id, "count": 2}],
            },
        )
        assert booking_response.status_code == 201
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
        # Create user first
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "calendar_filter_user",
                "name": "Calendar Filter User",
                "role": "owner",
            },
        )
        user = user_response.json()
        
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={"name": "Дом", "capacity": 4, "owner_id": user["id"]},
        )
        house_id = house_response.json()["id"]

        # Create tariff for bookings
        tariff_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Adult", "amount": 250},
        )
        tariff_id = tariff_response.json()["id"]

        # Create bookings in different periods
        response1 = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": [{"tariff_id": tariff_id, "count": 2}],
            },
        )
        assert response1.status_code == 201
        response2 = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house_id,
                "check_in": "2024-07-10",
                "check_out": "2024-07-15",
                "guests": [{"tariff_id": tariff_id, "count": 2}],
            },
        )
        assert response2.status_code == 201

        # Get calendar with date filter
        response = await client.get(
            f"/api/v1/houses/{house_id}/calendar?date_from=2024-06-01&date_to=2024-06-30"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["occupied_dates"]) == 1
        assert data["occupied_dates"][0]["check_in"] == "2024-06-01"
