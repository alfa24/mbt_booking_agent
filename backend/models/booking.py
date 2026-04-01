"""SQLAlchemy model for Booking entity."""

import enum

from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func

from backend.database import Base


class BookingStatus(str, enum.Enum):
    """Booking status enum."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(Base):
    """Booking model representing reservation requests."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    guests_planned = Column(JSON, nullable=False)
    guests_actual = Column(JSON)
    total_amount = Column(Integer)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"<Booking(id={self.id}, house_id={self.house_id}, "
            f"check_in={self.check_in}, status={self.status})>"
        )
