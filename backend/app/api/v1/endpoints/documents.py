import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.schemas.document import DocumentResponse
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStoreService
from app.core.config import settings
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.document import Document


router = APIRouter()

pdf_processor = PDFProcessor()
vector_store = VectorStoreService()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    doc_id = str(uuid.uuid4())

    file_path = os.path.join(
        settings.UPLOAD_DIR,
        f"{doc_id}_{file.filename}",
    )

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    chunks = pdf_processor.extract_text_and_split(
        file_path,
        doc_id,
    )

    if chunks:
        vector_store.add_documents(chunks)

    document = Document(
        id=doc_id,
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        content_type=file.content_type or "application/pdf",
        num_chunks=len(chunks),
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document