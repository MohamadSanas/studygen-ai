import uuid

from sqlalchemy.orm import Session

from app.models.conversation import Conversation


def create_conversation(
    db: Session,
    user_id: str,
    document_id: str,
    title: str = "New Conversation",
):
    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        document_id=document_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_user_conversation(
    db: Session,
    conversation_id: str,
    user_id: str,
):
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        .first()
    )