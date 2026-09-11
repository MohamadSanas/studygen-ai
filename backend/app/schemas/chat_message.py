from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChatMessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)