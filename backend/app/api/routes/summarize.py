from click import prompt
from app.services.llm_service import LLMService
from fastapi import APIRouter,Depends,HTTPException,File,UploadFile,Form

from pathlib import Path
import tempfile


from app.services.pdf_processor import PDFProcessor

router = APIRouter(
    prefix="/api",
    tags=["Summary"],
)

@router.post("/Summarize")
async def Summarize_pdf(file:UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400,detail="Invalid file type!!! only PDF files are allowed")
    

    file_bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = Path(temp_file.name)


    try:
        processor = PDFProcessor()

        documents = processor.extract_text_and_split(str(temp_file_path), document_id="summary-temp")

        if not documents:
            raise HTTPException(status_code=400,detail="PDF is empty or has no text")
        

        full_text = "\n\n".join(doc.page_content for doc in documents)

        llm = LLMService()

        prompt = f"""
            You are StudyGen AI, a study assistant.

            Summarize the following lecture material.

            Requirements:
            - Identify the main topics.
            - Explain the important concepts clearly.
            - Include important definitions.
            - Include important formulas when present.
            - Use headings and bullet points.
            - Do not invent information.
            - Keep the summary useful for university exam preparation.

            LECTURE MATERIAL:

            {full_text}

            SUMMARY:
            """

        summary = await llm.generate_response(prompt)

        return {
            "file_name":file.filename,
            "summary":summary
        }

    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error while Summarizing PDF:{str(e)}")
    finally:
        if temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except:
                pass

@router.post("/Summary-chunks")
async def Summary_chunks(file:UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400,detail="Invalid file type!!! only PDF files are allowed")
    

    file_bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = Path(temp_file.name)


    try:
        processor = PDFProcessor()

        documents = processor.extract_text_and_split(str(temp_file_path), document_id="summary-temp")

        if not documents:
            raise HTTPException(status_code=400,detail="PDF is empty or has no text")
        

        full_text = "\n\n".join(doc.page_content for doc in documents)

        llm = LLMService()

        prompt = f"""
            You are StudyGen AI, a study assistant.

            Summarize the following lecture material.

            Requirements:
            - Identify the main topics.
            - Explain the important concepts clearly.
            - Include important definitions.
            - Include important formulas when present.
            - Use headings and bullet points.
            - Do not invent information.
            - Keep the summary useful for university exam preparation.

            LECTURE MATERIAL:

            {full_text}

            SUMMARY:
            """

        summary = await llm.generate_response(prompt)

        return {
            "file_name":file.filename,
            "summary":summary
        }

    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error while Summarizing PDF:{str(e)}")
    finally:
        if temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except:
                pass