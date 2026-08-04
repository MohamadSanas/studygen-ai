from fastapi import APIRouter
from app.schemas.quiz import QuizRequest, QuizResponse, QuizQuestion

router = APIRouter()

@router.post("/", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    sample_questions = [
        QuizQuestion(
            id=1,
            question="What is the main topic of the uploaded document?",
            options=["Option A", "Option B", "Option C", "Option D"],
            correct_answer="Option A",
            explanation="Option A represents the primary subject."
        )
    ]
    return QuizResponse(
        document_id=request.document_id,
        questions=sample_questions
    )
