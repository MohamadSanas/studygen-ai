import os
from typing import List, Optional, Tuple


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
            model_name=settings.EMBEDDING_MODEL,
        )

        self.vector_db = Chroma(
            collection_name="studygen_collection",
            collection_metadata={"hnsw:space": "cosine"},
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def add_documents(self,documents: List[Document],) -> List[str]:
        """
        Add a list of documents to the vector database.
        Returns a list of document IDs.
        """
        return self.vector_db.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        document_id: Optional[str] = None,
        k: int = 5,
    ) -> List[Document]:
        """
        Perform similarity search with optional document ID filtering.
        Returns a list of similar documents.
        """
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
    
    def similarity_search_with_score(self, query: str, document_id: Optional[str] = None, k: int = 5) -> List[Tuple[Document, float]]:
        filter_dict = (
            {"document_id": document_id}
            if document_id
            else None
        )

        return self.vector_db.similarity_search_with_score(
            query,
            filter=filter_dict,
            k=k,
        )
    
    