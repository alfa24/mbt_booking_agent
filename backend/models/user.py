"""SQLAlchemy model for User entity."""

import enum

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func

from backend.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""

    TENANT = "tenant"
    OWNER = "owner"
    BOTH = "both"


class User(Base):
    """User model representing tenants and owners."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.TENANT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.name})>"
