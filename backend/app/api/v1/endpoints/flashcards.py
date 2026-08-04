from fastapi import APIRouter
from app.schemas.flashcards import FlashcardRequest, FlashcardResponse, FlashcardItem

router = APIRouter()

@router.post("/", response_model=FlashcardResponse)
async def generate_flashcards(request: FlashcardRequest):
    sample_cards = [
        FlashcardItem(
            id=1,
            front="What is Retrieval-Augmented Generation (RAG)?",
            back="RAG combines search retrieval with generative LLM prompt context to answer questions."
        )
    ]
    return FlashcardResponse(
        document_id=request.document_id,
        cards=sample_cards
    )
