from fastapi import APIRouter
from app.api.v1.endpoints import documents, chat, summary, quiz, flashcards

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat & RAG"])
api_router.include_router(summary.router, prefix="/summary", tags=["Summarization"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz Generation"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards"])
