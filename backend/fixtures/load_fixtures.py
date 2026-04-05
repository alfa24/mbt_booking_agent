"""Load demo data fixtures into database.

Usage:
    python -m backend.fixtures.load_fixtures
"""

import asyncio
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from backend.database import AsyncSessionLocal
from backend.models import User, House, Tariff, Booking, ConsumableNote


FIXTURES_DIR = Path(__file__).parent
FIXTURES_FILE = FIXTURES_DIR / "demo_data.json"


async def load_fixtures() -> None:
    """Load demo data from JSON file into database."""
    with open(FIXTURES_FILE, encoding="utf-8") as f:
        data = json.load(f)

    async with AsyncSessionLocal() as session:
        # Load users
        user_map = {}  # telegram_id -> User
        for user_data in data["users"]:
            stmt = select(User).where(User.telegram_id == user_data["telegram_id"])
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    telegram_id=user_data["telegram_id"],
                    name=user_data["name"],
                    role=user_data["role"],
                )
                session.add(user)
                await session.flush()

            user_map[user.telegram_id] = user

        print(f"Loaded {len(user_map)} users")

        # Load houses
        house_map = {}  # name -> House
        for house_data in data["houses"]:
            stmt = select(House).where(House.name == house_data["name"])
            result = await session.execute(stmt)
            house = result.scalar_one_or_none()

            if not house:
                owner = user_map[house_data["owner_telegram_id"]]
                house = House(
                    name=house_data["name"],
                    description=house_data["description"],
                    capacity=house_data["capacity"],
                    owner_id=owner.id,
                    is_active=True,
                )
                session.add(house)
                await session.flush()

            house_map[house.name] = house

        print(f"Loaded {len(house_map)} houses")

        # Load tariffs
        tariff_map = {}  # name -> Tariff
        for tariff_data in data["tariffs"]:
            stmt = select(Tariff).where(Tariff.name == tariff_data["name"])
            result = await session.execute(stmt)
            tariff = result.scalar_one_or_none()

            if not tariff:
                tariff = Tariff(
                    name=tariff_data["name"],
                    amount=tariff_data["amount"],
                )
                session.add(tariff)
                await session.flush()

            tariff_map[tariff.name] = tariff

        print(f"Loaded {len(tariff_map)} tariffs")

        # Load bookings
        today = date.today()
        booking_count = 0
        for booking_data in data["bookings"]:
            house = house_map[booking_data["house_name"]]
            tenant = user_map[booking_data["tenant_telegram_id"]]

            check_in = today + timedelta(days=booking_data["check_in_offset"])
            check_out = today + timedelta(days=booking_data["check_out_offset"])

            # Build guests_planned with tariff IDs
            guests_planned = []
            for guest in booking_data["guests_planned"]:
                tariff = tariff_map[guest["tariff_name"]]
                guests_planned.append({
                    "tariff_id": tariff.id,
                    "count": guest["count"],
                })

            booking = Booking(
                house_id=house.id,
                tenant_id=tenant.id,
                check_in=check_in,
                check_out=check_out,
                guests_planned=guests_planned,
                total_amount=booking_data["total_amount"],
                status=booking_data["status"],
            )
            session.add(booking)
            booking_count += 1

        await session.flush()
        print(f"Loaded {booking_count} bookings")

        # Load consumable notes
        note_count = 0
        for note_data in data["consumable_notes"]:
            house = house_map[note_data["house_name"]]
            creator = user_map[note_data["creator_telegram_id"]]

            note = ConsumableNote(
                house_id=house.id,
                created_by=creator.id,
                name=note_data["name"],
                comment=note_data["comment"],
            )
            session.add(note)
            note_count += 1

        await session.commit()
        print(f"Loaded {note_count} consumable notes")

    print("\nFixtures loaded successfully!")


def main() -> None:
    """Entry point for loading fixtures."""
    asyncio.run(load_fixtures())


if __name__ == "__main__":
    main()
