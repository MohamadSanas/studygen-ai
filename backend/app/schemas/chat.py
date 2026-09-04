from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    document_id: Optional[str] = None
    question: str
    chat_history: List[dict] = Field(default_factory=list)


class SourceChunk(BaseModel):
    page: Optional[int] = None
    content: str
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = Field(default_factory=list)