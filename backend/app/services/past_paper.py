from pydantic import BaseModel

class ExamQuestion(BaseModel):
    year: int
    question_number: int
    question_text: str
    answer: int | None = None

class PastPaper(BaseModel):
    document_id: str
    year: int | None = None
    questions: list[ExamQuestion]