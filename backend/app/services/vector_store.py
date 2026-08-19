import os
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.core.config import settings


class VectorStoreService:

    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY

        os.makedirs(
            self.persist_directory,
            exist_ok=True,
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def add_documents(
        self,
        documents: List[Document],
    ):
        self.vector_db.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        document_id: Optional[str] = None,
        k: int = 4,
    ):
        filter_dict = (
            {"document_id": document_id}
            if document_id
            else None
        )

        return self.vector_db.similarity_search(
            query,
            k=k,
            filter=filter_dict,
        )