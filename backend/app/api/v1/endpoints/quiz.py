from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.schemas.quiz import QuizResponse, QuizRequest, QuizQuestion
from app.models.user import User
from app.models.document import Document
from app.api.dependencies import get_current_user, get_db
from app.services.vector_service import VectorService
from app.services.llm_service_qwen_local import QwenLLMServiceLocal

router = APIRouter()

vector_service = VectorService()
llm = QwenLLMServiceLocal()


@router.post("/", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check document ownership
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

    # Retrieve relevant chunks from ChromaDB
    retrieved_docs = vector_service.similarity_search(
        query="main concepts, definitions, important facts and key topics",
        k=max(request.num_questions * 2, 10),
        document_id=request.document_id,
    )

    if not retrieved_docs:
        raise HTTPException(
            status_code=400,
            detail="No content found for this document.",
        )

    context = "\n\n".join(
        doc.page_content for doc in retrieved_docs
    )

    # Ask Qwen to generate the quiz
    prompt = f"""
        Generate {request.num_questions} multiple-choice questions
        from the provided lecture material.

        Difficulty: {request.difficulty}

        Requirements:
        - Generate exactly {request.num_questions} questions.
        - Each question must have exactly 4 options.
        - Only ONE option must be correct.
        - Include the correct answer.
        - Include a short explanation.
        - Questions must be based ONLY on the lecture material.
        - Do not invent information.
        - Return ONLY valid JSON.
        - Do not use Markdown.
        - Do not include ```json or ```.

        Use exactly this JSON structure:

        {{
            "questions": [
                {{
                    "id": 1,
                    "question": "Question text",
                    "options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ],
                    "correct_answer": "Option A",
                    "explanation": "Explanation"
                }}
            ]
        }}

        LECTURE MATERIAL:
        {context}
        """

    try:
        result = await llm.generate(
            question=prompt,
            context=context,
            chat_history=[],
        )

        # Remove accidental Markdown code fences
        result = result.strip()

        if result.startswith("```"):
            result = result.replace("```json", "")
            result = result.replace("```", "")
            result = result.strip()

        quiz_data = json.loads(result)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid JSON for the quiz.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quiz generation failed: {str(e)}",
        )

    # Convert generated questions into Pydantic objects
    try:
        questions = [
            QuizQuestion(**question)
            for question in quiz_data["questions"]
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid quiz format returned by Qwen: {str(e)}",
        )

    return QuizResponse(
        document_id=document.id,
        questions=questions,
    )