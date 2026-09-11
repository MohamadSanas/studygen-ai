from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
)
from app.services.conversation_service import create_conversation

from app.models.conversation import Conversation
from app.models.chat_message import ChatMessage
from app.schemas.chat_message import ChatMessageResponse


router = APIRouter()


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == request.document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    conversation = create_conversation(
        db=db,
        user_id=current_user.id,
        document_id=document.id,
        title=request.title,
    )

    return conversation


@router.get("/{conversation_id}/messages",response_model=List[ChatMessageResponse],
)

def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return messages