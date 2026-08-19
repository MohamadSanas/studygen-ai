from pathlib import Path
from typing import List

from langchain_core.documents import Document
from pypdf import PdfReader

from app.schemas.past_paper import ExamPaper
from app.services.llm_service import LLMService


class PastPaperProcessor:

    def __init__(self):
        self.llm_service = LLMService()

    def extract_pages(
        self,
        file_path: str | Path,
        document_id: str
    ) -> List[Document]:
        """
        Extract text from every page of the PDF.
        Each page is returned as a LangChain Document.
        """

        reader = PdfReader(file_path)

        documents: List[Document] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            text = text.strip()

            if not text:
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "document_id": document_id,
                        "page": page_number,
                    },
                )
            )

        return documents

    async def process(
        self,
        file_path: str,
        document_id: str,
        year: int | None = None,
    ) -> ExamPaper:
        """
        Process an entire past-paper PDF and extract its
        structured exam questions.
        """

        # ---------------------------------------------------------
        # 1. Extract PDF pages
        # ---------------------------------------------------------

        pages = self.extract_pages(
            file_path,
            document_id,
        )

        if not pages:
            raise ValueError(
                f"No readable text was extracted from PDF: {file_path}"
            )

        print("=" * 80)
        print(f"PDF: {file_path}")
        print(f"Pages extracted: {len(pages)}")
        print("=" * 80)

        # ---------------------------------------------------------
        # 2. Display extracted page text for debugging
        # ---------------------------------------------------------

        for page in pages:
            page_number = page.metadata.get("page")

            print(f"\n--- PAGE {page_number} ---")
            print(page.page_content)
            print(f"--- END PAGE {page_number} ---")

        # ---------------------------------------------------------
        # 3. Combine all pages
        # ---------------------------------------------------------

        full_text = "\n\n".join(
            f"--- PAGE {page.metadata.get('page')} ---\n"
            f"{page.page_content}"
            for page in pages
        )

        print("\n" + "=" * 80)
        print(f"FULL TEXT LENGTH: {len(full_text)} characters")
        print("=" * 80)

        # ---------------------------------------------------------
        # 4. Build extraction prompt
        # ---------------------------------------------------------

        prompt = f"""
You are an expert university examination-paper parser.

Your task is to extract the COMPLETE exam paper from the text below.

IMPORTANT:
- Extract ALL questions in the paper.
- Do NOT stop after Question 1.
- Preserve the original question numbering.
- Preserve hierarchical numbering such as:
  1
  1.1
  1.2
  2
  2.1
  2.2
- Preserve subquestion numbering such as:
  a
  b
  c
  i
  ii
  iii
- Extract the complete question text.
- Do NOT summarize questions.
- Do NOT invent missing questions.
- Extract context/background paragraphs when they belong to a question.
- Extract marks when explicitly shown.
- If marks are not explicitly available, use null.
- Preserve the order in which questions appear in the paper.
- If a question continues across pages, combine the text.
- Return the complete structured ExamPaper object.

The paper title should be extracted from the examination paper.

The year should be {year if year is not None else "extracted from the paper"}.

PAST PAPER TEXT:

{full_text}
"""

        # ---------------------------------------------------------
        # 5. Ask LLM for structured ExamPaper
        # ---------------------------------------------------------

        print("\n" + "=" * 80)
        print("SENDING COMPLETE PAPER TO LLM")
        print("=" * 80)

        result = await self.llm_service.generate_structured(
            prompt,
            ExamPaper,
        )

        # ---------------------------------------------------------
        # 6. Debug LLM result
        # ---------------------------------------------------------

        print("\n" + "=" * 80)
        print("LLM STRUCTURED RESULT")
        print("=" * 80)

        print(result)

        # ---------------------------------------------------------
        # 7. Validate extracted questions
        # ---------------------------------------------------------

        valid_questions = [
            question
            for question in result.questions
            if (
                question.question_number is not None
                or question.text is not None
                or question.context is not None
                or question.subquestions
            )
        ]

        print("\n" + "=" * 80)
        print(f"QUESTIONS EXTRACTED: {len(valid_questions)}")
        print("=" * 80)

        for question in valid_questions:
            print(
                f"Question: {question.question_number} | "
                f"Text: {question.text} | "
                f"Subquestions: {len(question.subquestions)}"
            )

        # ---------------------------------------------------------
        # 8. Return final ExamPaper
        # ---------------------------------------------------------

        return ExamPaper(
            paper_title=result.paper_title or "",
            year=year if year is not None else result.year,
            questions=valid_questions,
        )