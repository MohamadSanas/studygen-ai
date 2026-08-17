from pydantic import BaseModel

class ExamQuestion(BaseModel):
    question_number:str
    context:str | None = None
    text:str
    marks:int | None = None
    total_marks:str | None = None
    

class ExamPaper(BaseModel):
    paper_title: str
    year: int | None = None
    questions: list[ExamQuestion]