import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.quiz import QuizResponse, QuizRequest, QuizQuestion as QuizQuestionSchema
from app.models.user import User
from app.models.document import Document
from app.models.quiz import Quiz as QuizModel, QuizQuestion as QuizQuestionModel
from app.api.dependencies import get_current_user, get_db
from app.services.vector_store import VectorStoreService
from app.services.llm_service_qwen_local import QwenLLMServiceLocal

router = APIRouter()

vector_store = VectorStoreService()
llm = QwenLLMServiceLocal()


@router.post("/", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),):
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

    # 2. Retrieve relevant chunks from ChromaDB
    retrieved_docs = vector_store.similarity_search(
        query="main concepts, definitions, important facts and key topics",
        k=max(request.num_questions * 2, 10),
        document_id=request.document_id,
    )

    if not retrieved_docs:
        raise HTTPException(
            status_code=400,
            detail="No content found for this document.",
        )

    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    # 3. Prompt Qwen to generate structured JSON quiz
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

        # Clean accidental Markdown code fences
        result = result.strip()
        if result.startswith("```"):
            result = result.replace("```json", "").replace("```", "").strip()

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

    # 4. Parse questions into Pydantic schemas
    try:
        questions_schema = [
            QuizQuestionSchema(**q) for q in quiz_data["questions"]
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid quiz format returned by LLM: {str(e)}",
        )

    # 5. Persist Quiz & Questions to PostgreSQL
    new_quiz = QuizModel(
        user_id=current_user.id,
        document_id=document.id,
        title=f"Quiz: {document.filename}",
        difficulty=request.difficulty or "medium",
        num_questions=len(questions_schema),
    )
    db.add(new_quiz)
    db.flush()  # Populates new_quiz.id before committing

    for q in questions_schema:
        db_question = QuizQuestionModel(
            quiz_id=new_quiz.id,
            question_number=q.id,
            question_text=q.question,
            options=q.options,
            correct_answer=q.correct_answer,
            explanation=q.explanation,
        )
        db.add(db_question)

    db.commit()
    db.refresh(new_quiz)

    return QuizResponse(
        id=new_quiz.id,
        document_id=document.id,
        title=new_quiz.title,
        difficulty=new_quiz.difficulty,
        created_at=new_quiz.created_at,
        questions=questions_schema,
    )


@router.get("/{document_id}", response_model=List[QuizResponse])
def get_quizzes_for_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all previously generated quizzes for a specific document."""
    quizzes = (
        db.query(QuizModel)
        .filter(
            QuizModel.document_id == document_id,
            QuizModel.user_id == current_user.id,
        )
        .order_by(QuizModel.created_at.desc())
        .all()
    )

    results = []
    for q in quizzes:
        questions = [
            QuizQuestionSchema(
                id=item.question_number,
                question=item.question_text,
                options=item.options,
                correct_answer=item.correct_answer,
                explanation=item.explanation,
            )
            for item in q.questions
        ]
        results.append(
            QuizResponse(
                id=q.id,
                document_id=q.document_id,
                title=q.title,
                difficulty=q.difficulty,
                created_at=q.created_at,
                questions=questions,
            )
        )

    return results
