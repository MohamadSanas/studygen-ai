from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.document import Document
from pathlib import Path
import tempfile

from sqlalchemy.orm import Session

from app.services.llm_service_qwen import QwenLLMService
from app.services.chat_history_service import get_chat_history
from app.services.pdf_processor import PDFProcessor


router = APIRouter()


@router.post("/")
async def summarize_pdf(
    document_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # Return existing summary if already generated
    if document.summary:
        return {
            "file_name": document.filename,
            "summary": document.summary,
        }

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed.",
        )

    file_bytes = await file.read()

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False,
    ) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = Path(temp_file.name)

    try:
        processor = PDFProcessor()

        documents = processor.extract_text_and_split(
            str(temp_file_path),
            document_id="summary-temp",
        )

        print(f"Total chunks: {len(documents)}")

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="PDF is empty or has no text",
            )

        pages = sorted(
            set(doc.metadata.get("page") for doc in documents)
        )

        print(f"Pages found: {pages}")
        print(f"Total pages found: {len(pages)}")

        full_text = "\n\n".join(
            doc.page_content
            for doc in documents
        )

        llm = QwenLLMService()

        question = """
            Create a clear, exam-oriented summary of the lecture material.

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
            - Use # for headings.
            - Use **text** for bold.
            - Use - for bullet points.
            - Use LaTeX for mathematical formulas, for example:
            $$y = mx + b$$
        """

        chat_history = get_chat_history(
            db=db,
            conversation_id="summary-temp",
        )

        summary = await llm.generate(
            question=question,
            context=full_text,
            chat_history=chat_history,
        )

        # Save generated summary to PostgreSQL
        document.summary = summary
        db.commit()
        db.refresh(document)

        return {
            "file_name": document.filename,
            "summary": summary,
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Summary error: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Error while summarizing PDF: {str(e)}",
        )

    finally:
        if temp_file_path.exists():
            temp_file_path.unlink()