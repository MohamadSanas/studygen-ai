from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk
from app.services.vector_store import VectorStoreService
from app.services.llm_service_qwen import QwenLLMService

router = APIRouter()
vector_store = VectorStoreService()
llm_qwen = QwenLLMService()

@router.post("/", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):
    docs = vector_store.similarity_search(
        query=request.question,
        document_id=request.document_id,
        k=4
    )
    
    context = "\n\n".join([doc.page_content for doc in docs])
    
    if not docs:
        raise HTTPException(status_code=404, detail="No relevant document context found.")

    try:
        answer = await llm_qwen.generate(
            question=request.question,
            context=context
        )
    except Exception as e:
        print(f"Error calling Qwen LLM: {e}")
        # Fallback to simple context response if LLM fails
        answer = f"Based on your document context:\n\n{context[:300]}..."

    sources = [
        SourceChunk(
            page=doc.metadata.get("page"),
            content=doc.page_content[:200] + "..."
        )
        for doc in docs
    ]

    return ChatResponse(
        answer=answer,
        sources=sources
    )
