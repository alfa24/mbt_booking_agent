"""SQLAlchemy model for Tariff entity."""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from backend.database import Base


class Tariff(Base):
    """Tariff model representing guest pricing tiers."""

    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Tariff(id={self.id}, name={self.name}, amount={self.amount})>"
