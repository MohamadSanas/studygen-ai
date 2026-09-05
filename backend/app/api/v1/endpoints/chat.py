from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk
from app.services.vector_store import VectorStoreService
from app.services.llm_service_qwen import QwenLLMService


router = APIRouter()

vector_store = VectorStoreService()
llm_qwen = QwenLLMService()


@router.post("/", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):

    # 1. Retrieve relevant document chunks
    docs = vector_store.similarity_search(
        query=request.question,
        document_id=request.document_id,
        k=4
    )

    # 2. Check whether relevant chunks were found
    if not docs:
        raise HTTPException(
            status_code=404,
            detail="No relevant document context found."
        )

    # 3. Combine retrieved chunks into context
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # 4. Generate answer using Qwen
    try:
        answer = await llm_qwen.generate(
            question=request.question,
            context=context
        )

    except Exception as e:
        print(f"Error calling Qwen LLM: {e}")

        # Fallback response
        answer = (
            "The LLM could not generate an answer. "
            "Here is the relevant document context:\n\n"
            f"{context[:300]}..."
        )

    # 5. Prepare source information
    sources = [
        SourceChunk(
            page=doc.metadata.get("page"),
            content=doc.page_content[:200] + "..."
        )
        for doc in docs
    ]

    # 6. Return answer and sources
    return ChatResponse(
        answer=answer,
        sources=sources
    ) 