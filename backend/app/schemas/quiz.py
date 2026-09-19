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
    id: Optional[str]=None
    document_id: str
    title: Optional[str]=None
    difficulty: Optional[str]="medium"
    questions: List[QuizQuestion]
    class config:
        from_attributes = True


class EssayQuestion(BaseModel):
    document_id: str
    question: str
    answer : str
    explanation: str

class EssayQuestionRequest(BaseModel):
    document_id: str
    difficulty: Optional[str] = "Hard"

class EssayQuestionResponse(BaseModel):
    document_id: str
    questions: List[EssayQuestion]