import uuid

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage


def save_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
):
    message = ChatMessage(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_chat_history(
    db: Session,
    conversation_id: str,
):
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.conversation_id == conversation_id
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )