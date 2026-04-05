"""SQLAlchemy models for Chat and ChatMessage entities."""

from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.database import Base


class Chat(Base):
    """Chat model representing a conversation thread."""

    __tablename__ = "chats"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, user_id={self.user_id}, title={self.title})>"


class ChatMessage(Base):
    """ChatMessage model representing individual messages in a chat."""

    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant' | 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, chat_id={self.chat_id}, role={self.role})>"
