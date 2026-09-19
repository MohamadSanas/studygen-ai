from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FlashcardItem(BaseModel):
    id: Optional[str] = None
    front: str
    back: str
    mastery_level: int = 0

    class Config:
        from_attributes = True


class FlashcardRequest(BaseModel):
    document_id: str
    num_cards: int = 8


class FlashcardResponse(BaseModel):
    id: Optional[str] = None
    document_id: str
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    cards: List[FlashcardItem]

    class Config:
        from_attributes = True


class MasteryUpdateRequest(BaseModel):
    mastery_level: int  # 0 to 5
