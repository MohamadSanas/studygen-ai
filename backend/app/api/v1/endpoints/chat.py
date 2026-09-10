from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk
from app.services.vector_store import VectorStoreService
from app.services.llm_service_qwen import QwenLLMService
from app.services.chat_history_service import (
    get_chat_history,
    save_message,
)
from app.services.conversation_service import get_user_conversation
from app.api.dependencies import get_current_user, get_db
from app.models.user import User


router = APIRouter()

vector_store = VectorStoreService()
llm_qwen = QwenLLMService()


@router.post("/", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify that the conversation belongs to the logged-in user
    conversation = get_user_conversation(
        db=db,
        conversation_id=request.conversation_id,
        user_id=current_user.id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    # Make sure the conversation belongs to the requested document
    if conversation.document_id != request.document_id:
        raise HTTPException(
            status_code=400,
            detail="Conversation does not belong to this document.",
        )

    # Retrieve relevant PDF chunks from ChromaDB
    docs = vector_store.similarity_search(
        query=request.question,
        document_id=request.document_id,
        k=4,
    )

    if not docs:
        return ChatResponse(
            answer="No relevant document context found.",
            sources=[],
        )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # Retrieve conversation history from PostgreSQL
    history = get_chat_history(
        db=db,
        conversation_id=request.conversation_id,
    )

    chat_history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in history
    ]

    try:
        answer = await llm_qwen.generate(
            question=request.question,
            context=context,
            chat_history=chat_history,
        )

    except Exception as e:
        print(f"Error calling Qwen LLM: {e}")

        answer = (
            "The LLM could not generate an answer. "
            "Here is the relevant document context:\n\n"
            f"{context[:300]}..."
        )

    # Save user message
    save_message(
        db=db,
        conversation_id=request.conversation_id,
        role="user",
        content=request.question,
    )

    # Save assistant message
    save_message(
        db=db,
        conversation_id=request.conversation_id,
        role="assistant",
        content=answer,
    )

    sources = [
        SourceChunk(
            page=doc.metadata.get("page"),
            content=doc.page_content[:200] + "...",
        )
        for doc in docs
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
    )