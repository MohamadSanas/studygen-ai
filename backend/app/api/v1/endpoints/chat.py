from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk
from app.services.vector_store import VectorStoreService

router = APIRouter()
vector_store = VectorStoreService()

@router.post("/", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):
    docs = vector_store.similarity_search(
        query=request.question,
        document_id=request.document_id,
        k=4
    )
    
    context = "\n\n".join([doc.page_content for doc in docs])
    sources = [
        SourceChunk(
            page=doc.metadata.get("page"),
            content=doc.page_content[:200] + "..."
        )
        for doc in docs
    ]

    answer = f"Based on your document context:\n\n{context[:300]}..." if docs else "No relevant document context found."

    return ChatResponse(
        answer=answer,
        sources=sources
    )
