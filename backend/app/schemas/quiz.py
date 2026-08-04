from pydantic import BaseModel
from typing import List, Optional

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None

class QuizRequest(BaseModel):
    document_id: str
    num_questions: int = 5
    difficulty: Optional[str] = "medium"

class QuizResponse(BaseModel):
    document_id: str
    questions: List[QuizQuestion]
