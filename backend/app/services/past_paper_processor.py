from app.schemas.past_paper import ExamPaper
from pathlib import Path

from app.services.pdf_processor import PDFProcessor
from app.services.llm_service import LLMService
from app.services.past_paper import PastPaper

class PastPaperProcessor:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.llm_service = LLMService()
    
    async def process(self, file_path:str, document_id:str, year:int |None =None,) -> PastPaper :
        documents = self.pdf_processor.extract_text_and_split(str(file_path), str(document_id),)
        
        full_text = "\n\n".join(doc.page_content for doc in documents)

        prompt = f"""
            You are an exam paper parser.

            Extract all exam questions from the following past paper.

            Rules:
            - Preserve the original question numbering.
            - Preserve subquestions such as (a), (b), (i), (ii).
            - Do not invent questions.
            - Extract the question text as accurately as possible.
            - Extract marks when explicitly available.
            - If marks are not available, use null.
            - Return only the structured result.

            PAST PAPER:

            {full_text}


            """
        #response  = await self.llm_service.generate(prompt)

        result = await self.llm_service.generate_structured(
            prompt,
            ExamPaper
        )   

        print(result)

        return ExamPaper(
            paper_title=result.paper_title,
            year=year,
            questions=result.questions,
        )

