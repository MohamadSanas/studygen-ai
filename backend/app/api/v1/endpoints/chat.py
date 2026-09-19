from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk
from app.services.hybrid_search import HybridSearchService
from app.services.llm_service import llm_service
from app.services.chat_history_service import (
    get_chat_history,
    save_message,
)
from app.services.conversation_service import get_user_conversation
from app.api.dependencies import get_current_user, get_db
from app.models.user import User

router = APIRouter()

hybrid_search = HybridSearchService()
llm = llm_service


@router.post("/", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Verify that the conversation belongs to the logged-in user
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

    # 2. Make sure the conversation belongs to the requested document
    if conversation.document_id != request.document_id:
        raise HTTPException(
            status_code=400,
            detail="Conversation does not belong to this document.",
        )

    # 3. Retrieve top-4 chunks using 2-Stage Hybrid Search (Dense + BM25 + FlashRank)
    ranked_chunks = hybrid_search.search(
        query=request.question,
        document_id=request.document_id,
        top_k=4,
        candidate_pool=15,
    )

    if not ranked_chunks:
        return ChatResponse(
            answer="I couldn't find any relevant information in this document.",
            sources=[],
        )

    context = "\n\n---\n\n".join(chunk["content"] for chunk in ranked_chunks)

    # 4. Retrieve conversation history from PostgreSQL
    history = get_chat_history(
        db=db,
        conversation_id=request.conversation_id,
    )

    chat_history = [
        {"role": message.role, "content": message.content}
        for message in history
    ]

    system_prompt = (
        "You are StudyGen AI, an expert university study assistant. "
        "Answer the user's question accurately using ONLY the provided lecture material. "
        "If the answer is not in the material, state clearly: "
        "'I couldn't find this information in the uploaded document.' "
        "Keep your explanations clear, structured, and exam-oriented."
    )

    try:
        answer = await llm.generate(
            question=request.question,
            context=context,
            chat_history=chat_history,
            system_prompt=system_prompt,
        )
    except Exception as e:
        print(f"Error calling LLM: {e}")
        answer = (
            "The assistant could not generate an answer due to an inference error. "
            f"Here is the most relevant section found:\n\n{context[:300]}..."
        )

    # 5. Persist messages to database
    save_message(
        db=db,
        conversation_id=request.conversation_id,
        role="user",
        content=request.question,
    )
    save_message(
        db=db,
        conversation_id=request.conversation_id,
        role="assistant",
        content=answer,
    )

    # 6. Format source chunks with relevance scores
    sources = [
        SourceChunk(
            page=chunk["metadata"].get("page"),
            content=chunk["content"][:200] + "...",
            score=chunk.get("score"),
        )
        for chunk in ranked_chunks
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
    )
