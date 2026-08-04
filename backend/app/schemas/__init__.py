# StudyGen AI Backend Schemas
# Contains Pydantic models for API request/response validation

from .document import DocumentBase, DocumentCreate, DocumentResponse
from .chat import ChatRequest, ChatResponse, SourceChunk
from .quiz import QuizQuestion, QuizRequest, QuizResponse
from .flashcards import FlashcardItem, FlashcardRequest, FlashcardResponse
