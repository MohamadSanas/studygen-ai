from pydantic import BaseModel


class ExamQuestion(BaseModel):
    question_number: str
    text: str | None = None
    context: str | None = None
    marks: int | None = None
    total_marks: str | None = None
    subquestions: list["ExamQuestion"] = []


class ExamPaper(BaseModel):
    paper_title: str
    year: int | None = None
    questions: list[ExamQuestion]