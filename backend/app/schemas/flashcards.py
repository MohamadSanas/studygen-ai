from pydantic import BaseModel
from typing import List, Optional

class FlashcardItem(BaseModel):
    id: int
    front: str
    back: str

class FlashcardRequest(BaseModel):
    document_id: str
    num_cards: int = 10

class FlashcardResponse(BaseModel):
    document_id: str
    cards: List[FlashcardItem]
