import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.document import DocumentResponse
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStoreService
from app.core.config import settings

router = APIRouter()
pdf_processor = PDFProcessor()
vector_store = VectorStoreService()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    chunks = pdf_processor.extract_text_and_split(file_path, doc_id)
    if chunks:
        vector_store.add_documents(chunks)

    return {
        "id": doc_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_path": file_path,
        "num_chunks": len(chunks),
        "created_at": "2026-08-04T00:00:00Z"
    }
