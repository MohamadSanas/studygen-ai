from app.services.llm_service import LLMService
from fastapi import APIRouter,Depends,HTTPException,File,UploadFile,Form
from app.core.config import settings

from pathlib import Path
import tempfile


from app.services.pdf_processor import PDFProcessor

router = APIRouter()

@router.post("/")
async def summarize_pdf(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed."
        )

    file_bytes = await file.read()

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = Path(temp_file.name)

    try:
        processor = PDFProcessor()

        documents = processor.extract_text_and_split(
            str(temp_file_path),
            document_id="summary-temp"
        )

        print(f"Total chunks: {len(documents)}")

        pages = sorted(
            set(doc.metadata.get("page") for doc in documents)
        )

        print(f"Pages found: {pages}")
        print(f"Total pages found: {len(pages)}")

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="PDF is empty or has no text"
            )

        full_text = "\n\n".join(
            doc.page_content
            for doc in documents
        )

        llm = LLMService()

        prompt = f"""
            You are StudyGen AI, a university study assistant.

            Create a clear, exam-oriented summary of the lecture material below.

            Requirements:
            - Identify the main topics.
            - Explain important concepts clearly and concisely.
            - Include important definitions.
            - Include important formulas and equations when present.
            - Use Markdown headings.
            - Use Markdown bullet points and numbered lists where appropriate.
            - Use **bold** for important terms.
            - Preserve mathematical formulas using LaTeX.
            - Do not invent information that is not present in the lecture material.
            - Focus on information useful for university exam preparation.

            IMPORTANT FORMATTING RULES:
            - Return ONLY the Markdown summary.
            - Do NOT escape Markdown characters.
            - Use # for headings, not \\#.
            - Use **text** for bold, not \\*\\*text\\*\\*.
            - Use - for bullet points.
            - Use LaTeX for mathematical formulas, for example:
            $$y = mx + b$$

            LECTURE MATERIAL:

            {full_text}

            SUMMARY:
            """

        summary = await llm.generate(prompt)

        return {
            "file_name": file.filename,
            "summary": summary
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while summarizing PDF: {str(e)}"
        )

    finally:
        if temp_file_path.exists():
            temp_file_path.unlink()