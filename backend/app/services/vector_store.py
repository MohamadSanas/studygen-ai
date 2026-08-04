import os
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from app.core.config import settings

class VectorStoreService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_directory, exist_ok=True)
        self.embeddings = self._get_embedding_function()
        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def _get_embedding_function(self):
        if settings.GOOGLE_API_KEY:
            return GoogleGenerativeAIEmbeddings(
                google_api_key=settings.GOOGLE_API_KEY,
                model=settings.EMBEDDING_MODEL
            )
        elif settings.OPENAI_API_KEY:
            return OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        else:
            # Fallback to Sentence Transformers
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def add_documents(self, documents: List[Document]):
        self.vector_db.add_documents(documents)

    def similarity_search(self, query: str, document_id: Optional[str] = None, k: int = 4):
        filter_dict = {"document_id": document_id} if document_id else None
        return self.vector_db.similarity_search(query, k=k, filter=filter_dict)
