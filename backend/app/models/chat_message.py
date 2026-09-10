from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)

    conversation_id = Column(
        String,
        ForeignKey("conversations.id"),
        nullable=False,
        index=True,
    )

    role = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )