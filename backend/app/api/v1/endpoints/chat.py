from fastapi import APIRouter

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

    if not docs:
        return ChatResponse(
            answer="No relevant document context found.",
            sources=[]
        )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    try:
        answer = await llm_qwen.generate(
            question=request.question,
            context=context,
            chat_history=request.chat_history,
        )

    except Exception as e:
        print(f"Error calling Qwen LLM: {e}")

        answer = (
            "The LLM could not generate an answer. "
            "Here is the relevant document context:\n\n"
            f"{context[:300]}..."
        )

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