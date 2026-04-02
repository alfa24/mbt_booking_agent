"""Tests for booking API endpoints."""

import pytest


class TestCreateBooking:
    """Tests for POST /api/v1/bookings"""

    async def _create_test_data(self, client):
        """Helper to create user, house, and tariff for tests."""
        # Create user
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_user",
                "name": "Booking Test User",
                "role": "tenant",
            },
        )
        user = user_response.json()
        
        # Create house owner
        owner_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_owner",
                "name": "Booking Test Owner",
                "role": "owner",
            },
        )
        owner = owner_response.json()
        
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Test House",
                "capacity": 6,
                "owner_id": owner["id"],
            },
        )
        house = house_response.json()
        
        # Create tariff
        tariff_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Adult", "amount": 250},
        )
        tariff = tariff_response.json()
        
        return user, house, tariff

    @pytest.mark.asyncio
    async def test_create_booking_success(self, client):
        """Test creating a booking with valid data."""
        user, house, tariff = await self._create_test_data(client)
        
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["house_id"] == house["id"]
        assert data["tenant_id"] == user["id"]
        assert data["check_in"] == "2024-06-01"
        assert data["check_out"] == "2024-06-03"
        assert data["status"] == "pending"
        assert data["total_amount"] == 500  # 2 adults * 250
        assert len(data["guests_planned"]) == 1

    @pytest.mark.asyncio
    async def test_create_booking_invalid_dates(self, client):
        """Test creating a booking with check_in >= check_out."""
        user, house, tariff = await self._create_test_data(client)
        
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-03",
                "check_out": "2024-06-01",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_same_date(self, client):
        """Test creating a booking with check_in == check_out."""
        user, house, tariff = await self._create_test_data(client)
        
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-01",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_missing_guests(self, client):
        """Test creating a booking without guests."""
        user, house, tariff = await self._create_test_data(client)
        
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_empty_guests(self, client):
        """Test creating a booking with empty guests list."""
        user, house, tariff = await self._create_test_data(client)
        
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [],
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_date_conflict(self, client):
        """Test creating a booking with conflicting dates."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create first booking
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )

        # Try to create overlapping booking
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-12",
                "check_out": "2024-06-17",
                "guests": [{"tariff_id": tariff["id"], "count": 1}],
            },
        )
        assert response.status_code == 400
        assert "conflict" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_create_booking_different_house_no_conflict(self, client):
        """Test that bookings for different houses don't conflict."""
        user, house1, tariff = await self._create_test_data(client)
        
        # Create owner for second house
        owner2_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "owner2_user",
                "name": "Owner 2",
                "role": "owner",
            },
        )
        owner2 = owner2_response.json()
        
        # Create second house
        house2_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "House 2",
                "capacity": 6,
                "owner_id": owner2["id"],
            },
        )
        house2 = house2_response.json()
        
        # Create booking for house 1
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house1["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )

        # Create booking for house 2 with overlapping dates
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house2["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-12",
                "check_out": "2024-06-17",
                "guests": [{"tariff_id": tariff["id"], "count": 1}],
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_booking_amount_calculation(self, client):
        """Test amount calculation for different guest types."""
        user, house, tariff_adult = await self._create_test_data(client)
        
        # Create child tariff (free)
        tariff_child_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Child", "amount": 0},
        )
        tariff_child = tariff_child_response.json()
        
        # Create regular tariff
        tariff_regular_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Regular", "amount": 150},
        )
        tariff_regular = tariff_regular_response.json()
        
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [
                    {"tariff_id": tariff_child["id"], "count": 2},  # Children: free
                    {"tariff_id": tariff_adult["id"], "count": 2},  # Adults: 250 each
                    {"tariff_id": tariff_regular["id"], "count": 1},  # Regular: 150
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["total_amount"] == 650  # 0*2 + 250*2 + 150*1


class TestGetBooking:
    """Tests for GET /api/v1/bookings/{id}"""

    async def _create_test_data(self, client):
        """Helper to create user, house, and tariff for tests."""
        # Create user
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_user",
                "name": "Booking Test User",
                "role": "tenant",
            },
        )
        user = user_response.json()
        
        # Create house owner
        owner_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_owner",
                "name": "Booking Test Owner",
                "role": "owner",
            },
        )
        owner = owner_response.json()
        
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Test House",
                "capacity": 6,
                "owner_id": owner["id"],
            },
        )
        house = house_response.json()
        
        # Create tariff
        tariff_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Adult", "amount": 250},
        )
        tariff = tariff_response.json()
        
        return user, house, tariff

    @pytest.mark.asyncio
    async def test_get_booking_success(self, client):
        """Test getting an existing booking."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create booking first
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Get the booking
        response = await client.get(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == booking_id
        assert data["house_id"] == house["id"]

    @pytest.mark.asyncio
    async def test_get_booking_not_found(self, client):
        """Test getting a non-existent booking."""
        response = await client.get("/api/v1/bookings/999")
        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestListBookings:
    """Tests for GET /api/v1/bookings"""

    async def _create_test_data(self, client):
        """Helper to create user, house, and tariff for tests."""
        # Create user
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_user",
                "name": "Booking Test User",
                "role": "tenant",
            },
        )
        user = user_response.json()
        
        # Create house owner
        owner_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_owner",
                "name": "Booking Test Owner",
                "role": "owner",
            },
        )
        owner = owner_response.json()
        
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Test House",
                "capacity": 6,
                "owner_id": owner["id"],
            },
        )
        house = house_response.json()
        
        # Create tariff
        tariff_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Adult", "amount": 250},
        )
        tariff = tariff_response.json()
        
        return user, house, tariff

    async def _create_second_house(self, client, user):
        """Helper to create a second house."""
        # Create another owner
        owner2_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "owner2_user",
                "name": "Owner 2",
                "role": "owner",
            },
        )
        owner2 = owner2_response.json()
        
        house2_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "House 2",
                "capacity": 6,
                "owner_id": owner2["id"],
            },
        )
        return house2_response.json()

    @pytest.mark.asyncio
    async def test_list_bookings_empty(self, client):
        """Test listing bookings when none exist."""
        response = await client.get("/api/v1/bookings")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_bookings_with_data(self, client):
        """Test listing multiple bookings."""
        user, house1, tariff = await self._create_test_data(client)
        house2 = await self._create_second_house(client, user)
        
        # Create two bookings
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house1["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house2["id"],
                "tenant_id": user["id"],
                "check_in": "2024-07-01",
                "check_out": "2024-07-03",
                "guests": [{"tariff_id": tariff["id"], "count": 1}],
            },
        )

        response = await client.get("/api/v1/bookings")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_bookings_filter_by_house(self, client):
        """Test filtering bookings by house_id."""
        user, house1, tariff = await self._create_test_data(client)
        house2 = await self._create_second_house(client, user)
        
        # Create bookings for different houses
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house1["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house2["id"],
                "tenant_id": user["id"],
                "check_in": "2024-07-01",
                "check_out": "2024-07-03",
                "guests": [{"tariff_id": tariff["id"], "count": 1}],
            },
        )

        response = await client.get(f"/api/v1/bookings?house_id={house1['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["house_id"] == house1["id"]

    @pytest.mark.asyncio
    async def test_list_bookings_filter_by_status(self, client):
        """Test filtering bookings by status."""
        user, house1, tariff = await self._create_test_data(client)
        house2 = await self._create_second_house(client, user)
        
        # Create and cancel a booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house1["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]
        await client.delete(f"/api/v1/bookings/{booking_id}")

        # Create another booking (pending)
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house2["id"],
                "tenant_id": user["id"],
                "check_in": "2024-07-01",
                "check_out": "2024-07-03",
                "guests": [{"tariff_id": tariff["id"], "count": 1}],
            },
        )

        response = await client.get("/api/v1/bookings?status=cancelled")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_list_bookings_pagination(self, client):
        """Test pagination with limit and offset."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create multiple bookings with non-overlapping dates
        for i in range(5):
            response = await client.post(
                "/api/v1/bookings",
                json={
                    "house_id": house["id"],
                    "check_in": f"2024-07-{i*5+1:02d}",
                    "check_out": f"2024-07-{i*5+3:02d}",
                    "guests": [{"tariff_id": tariff["id"], "count": 1}],
                },
            )
            assert response.status_code == 201

        response = await client.get("/api/v1/bookings?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1


class TestUpdateBooking:
    """Tests for PATCH /api/v1/bookings/{id}"""

    async def _create_test_data(self, client):
        """Helper to create user, house, and tariff for tests."""
        # Create user
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_user",
                "name": "Booking Test User",
                "role": "tenant",
            },
        )
        user = user_response.json()
        
        # Create house owner
        owner_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_owner",
                "name": "Booking Test Owner",
                "role": "owner",
            },
        )
        owner = owner_response.json()
        
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Test House",
                "capacity": 6,
                "owner_id": owner["id"],
            },
        )
        house = house_response.json()
        
        # Create tariff
        tariff_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Adult", "amount": 250},
        )
        tariff = tariff_response.json()
        
        return user, house, tariff

    @pytest.mark.asyncio
    async def test_update_booking_dates(self, client):
        """Test updating booking dates."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Update dates
        response = await client.patch(
            f"/api/v1/bookings/{booking_id}",
            json={
                "check_in": "2024-06-05",
                "check_out": "2024-06-07",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["check_in"] == "2024-06-05"
        assert data["check_out"] == "2024-06-07"

    @pytest.mark.asyncio
    async def test_update_booking_guests(self, client):
        """Test updating guest composition."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Update guests (changes amount from 500 to 750)
        response = await client.patch(
            f"/api/v1/bookings/{booking_id}",
            json={
                "guests": [{"tariff_id": tariff["id"], "count": 3}],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_amount"] == 750
        assert len(data["guests_planned"]) == 1
        assert data["guests_planned"][0]["count"] == 3

    @pytest.mark.asyncio
    async def test_update_booking_not_found(self, client):
        """Test updating a non-existent booking."""
        response = await client.patch(
            "/api/v1/bookings/999",
            json={"check_in": "2024-06-05"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_booking_invalid_dates(self, client):
        """Test updating with invalid dates."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Try to update with invalid dates
        response = await client.patch(
            f"/api/v1/bookings/{booking_id}",
            json={
                "check_in": "2024-06-05",
                "check_out": "2024-06-04",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_booking_date_conflict(self, client):
        """Test updating with conflicting dates."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create first booking
        await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )

        # Create second booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-20",
                "check_out": "2024-06-25",
                "guests": [{"tariff_id": tariff["id"], "count": 1}],
            },
        )
        booking_id = create_response.json()["id"]

        # Try to update second booking to overlap with first
        response = await client.patch(
            f"/api/v1/bookings/{booking_id}",
            json={
                "check_in": "2024-06-12",
                "check_out": "2024-06-17",
            },
        )
        assert response.status_code == 400


class TestCancelBooking:
    """Tests for DELETE /api/v1/bookings/{id}"""

    async def _create_test_data(self, client):
        """Helper to create user, house, and tariff for tests."""
        # Create user
        user_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_user",
                "name": "Booking Test User",
                "role": "tenant",
            },
        )
        user = user_response.json()
        
        # Create house owner
        owner_response = await client.post(
            "/api/v1/users",
            json={
                "telegram_id": "booking_test_owner",
                "name": "Booking Test Owner",
                "role": "owner",
            },
        )
        owner = owner_response.json()
        
        # Create house
        house_response = await client.post(
            "/api/v1/houses",
            json={
                "name": "Test House",
                "capacity": 6,
                "owner_id": owner["id"],
            },
        )
        house = house_response.json()
        
        # Create tariff
        tariff_response = await client.post(
            "/api/v1/tariffs",
            json={"name": "Adult", "amount": 250},
        )
        tariff = tariff_response.json()
        
        return user, house, tariff

    @pytest.mark.asyncio
    async def test_cancel_booking_success(self, client):
        """Test cancelling a booking."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]

        # Cancel booking
        response = await client.delete(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_booking_not_found(self, client):
        """Test cancelling a non-existent booking."""
        response = await client.delete("/api/v1/bookings/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_already_cancelled(self, client):
        """Test cancelling an already cancelled booking."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create and cancel booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]
        await client.delete(f"/api/v1/bookings/{booking_id}")

        # Try to cancel again
        response = await client.delete(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == 400
        assert "already_cancelled" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_cancelled_booking_not_in_list(self, client):
        """Test that cancelled bookings don't appear in conflict checks."""
        user, house, tariff = await self._create_test_data(client)
        
        # Create and cancel booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": house["id"],
                "tenant_id": user["id"],
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": tariff["id"], "count": 2}],
            },
        )
        booking_id = create_response.json()["id"]
        await client.delete(f"/api/v1/bookings/{booking_id}")

        # Create new booking for same dates (should succeed)
        response = await client.post(
            "/api/v1/bookings",
            json={
                "house_id": 1,
                "check_in": "2024-06-10",
                "check_out": "2024-06-15",
                "guests": [{"tariff_id": 2, "count": 1}],
            },
        )
        assert response.status_code == 201
