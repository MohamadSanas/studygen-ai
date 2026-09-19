from typing import Dict, List, Optional
from app.services.hybrid_search import HybridSearchService
from app.services.llm_service import llm_service


class RAGService:
    def __init__(self):
        self.hybrid_search = HybridSearchService()
        self.llm = llm_service

    async def ask(
        self,
        question: str,
        document_id: Optional[str] = None,
        top_k: int = 4,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:
        """
        Executes grounded RAG:
        1. 2-Stage Hybrid Retrieval (Dense + BM25 + FlashRank).
        2. Context synthesis with citation metadata.
        3. Strict groundedness prompt to prevent hallucinations.
        """
        chat_history = chat_history or []

        # 1. 2-Stage Hybrid Retrieval & Re-ranking
        ranked_chunks = self.hybrid_search.search(
            query=question,
            document_id=document_id,
            top_k=top_k,
            candidate_pool=15,
        )

        if not ranked_chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded document for your question.",
                "sources": [],
            }

        # 2. Build structured context with source tags
        context_parts = []
        sources = []

        for chunk in ranked_chunks:
            meta = chunk.get("metadata", {})
            page = meta.get("page", 1)
            score = chunk.get("score", 0.0)
            content = chunk.get("content", "")

            context_parts.append(f"[Page {page} | Relevance: {score}]\n{content}")

            sources.append({
                "page": page,
                "score": score,
                "content": content[:200] + "...",
                "retrieval_method": chunk.get("retrieval_method", "hybrid"),
            })

        context = "\n\n---\n\n".join(context_parts)

        # 3. Grounded Generation Prompt
        system_prompt = (
            "You are StudyGen AI, an expert academic tutor and study assistant. "
            "Answer the user's question using ONLY the provided lecture material. "
            "If the answer cannot be deduced directly from the context, clearly state: "
            "'I couldn't find the answer in the uploaded lecture notes.' "
            "Cite the page number(s) where relevant information is found. "
            "Do not invent facts or extrapolate beyond what is stated."
        )

        answer = await self.llm.generate(
            question=question,
            context=context,
            chat_history=chat_history,
            system_prompt=system_prompt,
        )

        return {
            "answer": answer,
            "sources": sources,
        }


