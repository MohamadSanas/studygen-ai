from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SummaryRequest(BaseModel):
    document_id: str

class SummaryResponse(BaseModel):
    document_id: str
    summary: str

@router.post("/", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest):
    return SummaryResponse(
        document_id=request.document_id,
        summary="This is an AI-generated summary of the uploaded document."
    )
