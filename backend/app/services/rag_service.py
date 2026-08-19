from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService


class RAGService:

    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()

    async def ask(self, question: str, k: int = 4) -> dict:

        # 1. Retrieve relevant documents
        documents = self.vector_store.similarity_search(
            question,
            k=k
        )

        # 2. Build context
        context_parts = []

        for doc in documents:
            context_parts.append(
                f"""
                Source:
                Document: {doc.metadata.get("document_id")}
                Page: {doc.metadata.get("page")}
                Chunk: {doc.metadata.get("chunk_index")}

                Content:
                {doc.page_content}
                """
            )

        context = "\n\n".join(context_parts)

        # 3. Build prompt
        prompt = f"""
            You are StudyGen AI, an intelligent study assistant.

            Answer the user's question using ONLY the provided context.

            If the answer cannot be found in the context, say:
            "I couldn't find the answer in the uploaded document."

            Do not invent information.

            CONTEXT:
            {context}

            USER QUESTION:
            {question}

            ANSWER:
            """

        # 4. Generate answer
        answer = await self.llm_service.generate(prompt)

        # 5. Return answer + sources
        sources = [
            {
                "document_id": doc.metadata.get("document_id"),
                "page": doc.metadata.get("page"),
                "chunk_index": doc.metadata.get("chunk_index"),
            }
            for doc in documents
        ]

        return {
            "answer": answer,
            "sources": sources,
        }