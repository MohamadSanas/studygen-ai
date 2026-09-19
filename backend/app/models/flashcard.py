import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class FlashcardSet(Base):
    __tablename__ = "flashcard_sets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    document = relationship("Document")
    cards = relationship("Flashcard", back_populates="flashcard_set", cascade="all, delete-orphan")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    set_id = Column(String, ForeignKey("flashcard_sets.id"), nullable=False)
    front = Column(Text, nullable=False)  # Concept, term, or question
    back = Column(Text, nullable=False)   # Definition, explanation, formula
    mastery_level = Column(Integer, default=0)  # For spaced repetition (0-5)

    # Relationship
    flashcard_set = relationship("FlashcardSet", back_populates="cards")
