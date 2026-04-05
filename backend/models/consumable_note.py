"""SQLAlchemy model for ConsumableNote entity."""

from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.database import Base


class ConsumableNote(Base):
    """ConsumableNote model representing notes about consumables for houses."""

    __tablename__ = "consumable_notes"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<ConsumableNote(id={self.id}, house_id={self.house_id}, name={self.name})>"
