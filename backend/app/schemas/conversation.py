from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationCreate(BaseModel):
    document_id: str
    title: str = "New Conversation"


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    document_id: str
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)