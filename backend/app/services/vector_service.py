from langchain_chroma import Chroma

from app.services.embedding_service import EmbeddingService


class VectorService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = Chroma(
            collection_name="studygen_collection",
            collection_metadata={"hnsw:space": "cosine"},
            persist_directory="./chroma_db",
            embedding_function=self.embedding_service.embeddings,
        )

    def add_documents(self, documents):
        self.vector_store.add_documents(documents)

    def similarity_search(self, query:str, k:int=5):
        return self.vector_store.similarity_search(query, k=k)
        
    def create_vector_store(self, documents):
        self.vector_store = Chroma.from_documents(
            documents, 
            self.embedding_service.get_embeddings(),
            collection_name="studygen_collection",
            collection_metadata={"hnsw:space": "cosine"},
            persist_directory="./.venv/chroma_db"
        )

    def query_vector_store(self, query, k=5):
        if self.vector_store is None:
            self.vector_store = Chroma(
                collection_name="studygen_collection",
                collection_metadata={"hnsw:space": "cosine"},
                persist_directory="./.venv/chroma_db",
                embedding_function=self.embedding_service.get_embeddings(),
            )

        return self.vector_store.similarity_search(query, k=k)
