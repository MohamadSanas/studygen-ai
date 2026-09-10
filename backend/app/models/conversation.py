from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from app.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    document_id = Column(
        String,
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    title = Column(String, nullable=False, default="New Conversation")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )