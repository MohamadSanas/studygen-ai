from app.schemas import QuizQuestion
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.quiz import QuizResponse, QuizRequest
from app.models.user import User
from app.models.document import Document
from app.api.dependencies import get_current_user, get_db

router = APIRouter()


@router.post("/", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    document = (
        db.query(Document)
        .filter(
            Document.id == request.document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    sample_question = [
        QuizQuestion(
            id =1,
            question="What is the main topic of the uploaded document?",
            options=["Python", "Java", "C++", "JavaScript"],
            correct_answer="Python",
            explanation="Python is a high-level, interpreted programming language.",
        )
    ]

    return QuizResponse(
        document_id=document.id,
        questions=sample_question,
    )

    