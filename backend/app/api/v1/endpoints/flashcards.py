import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.flashcards import (
    FlashcardRequest,
    FlashcardResponse,
    FlashcardItem,
    MasteryUpdateRequest,
)
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import FlashcardSet as FlashcardSetModel, Flashcard as FlashcardModel
from app.api.dependencies import get_current_user, get_db
from app.services.vector_store import VectorStoreService
from app.services.llm_service_qwen_local import QwenLLMServiceLocal

router = APIRouter()

vector_store = VectorStoreService()
llm = QwenLLMServiceLocal()


@router.post("/", response_model=FlashcardResponse)
async def generate_flashcards(
    request: FlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Verify document ownership
    document = (
        db.query(Document)
        .filter(
            Document.id == request.document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2. Retrieve relevant lecture chunks from ChromaDB
    retrieved_docs = vector_store.similarity_search(
        query="key definitions, core concepts, formulas, terminology, and principles",
        k=max(request.num_cards * 2, 8),
        document_id=request.document_id,
    )

    if not retrieved_docs:
        raise HTTPException(
            status_code=400,
            detail="No content found for this document to generate flashcards.",
        )

    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    # 3. Prompt Qwen to generate structured JSON flashcards
    prompt = f"""
        Extract exactly {request.num_cards} essential study flashcards from the lecture material.
        
        Requirements:
        - Generate exactly {request.num_cards} cards.
        - "front": A concise question, key term, or concept to remember.
        - "back": A clear, accurate explanation, definition, or formula.
        - Base cards ONLY on the lecture material. Do not invent information.
        - Return ONLY valid JSON.
        - Do not use Markdown backticks (no ```json).

        Use exactly this JSON format:
        {{
            "cards": [
                {{
                    "front": "What is ...?",
                    "back": "..."
                }}
            ]
        }}

        LECTURE MATERIAL:
        {context}
        """

    try:
        result = await llm.generate(
            question=prompt,
            context=context,
            chat_history=[],
        )

        result = result.strip()
        if result.startswith("```"):
            result = result.replace("```json", "").replace("```", "").strip()

        data = json.loads(result)
        raw_cards = data.get("cards", [])

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="LLM returned invalid JSON for flashcards.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Flashcard generation failed: {str(e)}",
        )

    # 4. Save FlashcardSet and Flashcards to PostgreSQL
    new_set = FlashcardSetModel(
        user_id=current_user.id,
        document_id=document.id,
        title=f"Flashcards: {document.filename}",
    )
    db.add(new_set)
    db.flush()

    card_items: List[FlashcardItem] = []
    for card_data in raw_cards:
        db_card = FlashcardModel(
            set_id=new_set.id,
            front=card_data.get("front", ""),
            back=card_data.get("back", ""),
            mastery_level=0,
        )
        db.add(db_card)
        db.flush()

        card_items.append(
            FlashcardItem(
                id=db_card.id,
                front=db_card.front,
                back=db_card.back,
                mastery_level=db_card.mastery_level,
            )
        )

    db.commit()
    db.refresh(new_set)

    return FlashcardResponse(
        id=new_set.id,
        document_id=document.id,
        title=new_set.title,
        created_at=new_set.created_at,
        cards=card_items,
    )


@router.get("/{document_id}", response_model=List[FlashcardResponse])
def get_flashcard_sets(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve previously saved flashcard sets for this document."""
    sets = (
        db.query(FlashcardSetModel)
        .filter(
            FlashcardSetModel.document_id == document_id,
            FlashcardSetModel.user_id == current_user.id,
        )
        .order_by(FlashcardSetModel.created_at.desc())
        .all()
    )

    results = []
    for s in sets:
        cards = [
            FlashcardItem(
                id=c.id,
                front=c.front,
                back=c.back,
                mastery_level=c.mastery_level,
            )
            for c in s.cards
        ]
        results.append(
            FlashcardResponse(
                id=s.id,
                document_id=s.document_id,
                title=s.title,
                created_at=s.created_at,
                cards=cards,
            )
        )
    return results


@router.patch("/cards/{card_id}/mastery")
def update_card_mastery(
    card_id: str,
    payload: MasteryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user's mastery level for a specific card (0 to 5 for spaced repetition)."""
    card = (
        db.query(FlashcardModel)
        .join(FlashcardSetModel)
        .filter(
            FlashcardModel.id == card_id,
            FlashcardSetModel.user_id == current_user.id,
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    card.mastery_level = max(0, min(5, payload.mastery_level))
    db.commit()

    return {"status": "success", "card_id": card.id, "mastery_level": card.mastery_level}
