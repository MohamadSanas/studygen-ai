from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    content_type = Column(String, nullable=False)

    num_chunks = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )