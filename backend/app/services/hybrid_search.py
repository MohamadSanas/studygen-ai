import logging
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import re

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from flashrank import Ranker, RerankRequest

from app.services.vector_store import VectorStoreService
from app.core.config import settings

logger = logging.getLogger(__name__)


def tokenize_text(text: str) -> List[str]:
    """Simple alphanumeric tokenizer for BM25."""
    return re.findall(r"\w+", text.lower())


class BM25Index:
    """In-memory BM25 index over document chunks."""

    def __init__(self, documents: List[Document]):
        self.documents = documents
        self.corpus = [tokenize_text(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus else None

    def search(self, query: str, top_k: int = 15) -> List[Tuple[Document, float]]:
        if not self.bm25 or not self.documents:
            return []

        tokenized_query = tokenize_text(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        # Pair documents with their scores and sort descending
        doc_scores = list(zip(self.documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        return [(doc, score) for doc, score in doc_scores[:top_k] if score > 0]


class HybridSearchService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.reranker_enabled = getattr(settings, "RERANKER_ENABLED", True)

        # Initialize FlashRank Cross-Encoder
        try:
            self.ranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2", cache_dir="./chroma_db/flashrank_cache")
            logger.info("[HybridSearch] FlashRank re-ranker initialized successfully.")
        except Exception as e:
            logger.warning(f"[HybridSearch] FlashRank initialization failed: {e}. Falling back to RRF only.")
            self.ranker = None

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Document],
        sparse_results: List[Document],
        k: int = 60,
    ) -> List[Tuple[Document, float]]:
        """
        Merges dense and sparse ranked lists using Reciprocal Rank Fusion (RRF).
        RRF Score = 1 / (k + rank)
        """
        rrf_scores: Dict[str, float] = defaultdict(float)
        doc_map: Dict[str, Document] = {}

        # 1. Score dense vector results
        for rank, doc in enumerate(dense_results, start=1):
            doc_id = doc.page_content  # Use content as unique key
            doc_map[doc_id] = doc
            rrf_scores[doc_id] += 1.0 / (k + rank)

        # 2. Score sparse BM25 results
        for rank, doc in enumerate(sparse_results, start=1):
            doc_id = doc.page_content
            doc_map[doc_id] = doc
            rrf_scores[doc_id] += 1.0 / (k + rank)

        # Sort documents by accumulated RRF score
        sorted_docs = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        return [(doc_map[doc_id], score) for doc_id, score in sorted_docs]

    def search(
        self,
        query: str,
        document_id: Optional[str] = None,
        top_k: int = 4,
        candidate_pool: int = 15,
    ) -> List[Dict]:
        """
        2-Stage Retrieval:
        1. Retrieve top candidate pool using Dense (Chroma) + Sparse (BM25) with RRF.
        2. Re-rank candidate pool using FlashRank Cross-Encoder for top-k precision.
        """
        # Step 1: Dense Semantic Search via ChromaDB
        dense_docs = self.vector_store.similarity_search(
            query=query,
            k=candidate_pool,
            document_id=document_id,
        )

        # Step 2: Sparse BM25 Search over candidate pool or full doc
        # (We index retrieved candidates + related chunks to keep memory light and fast)
        bm25_index = BM25Index(dense_docs)
        sparse_ranked = bm25_index.search(query, top_k=candidate_pool)
        sparse_docs = [doc for doc, _ in sparse_ranked]

        # Step 3: Combine with Reciprocal Rank Fusion (RRF)
        fused_candidates = self._reciprocal_rank_fusion(dense_docs, sparse_docs, k=60)
        candidate_docs = [doc for doc, _ in fused_candidates[:candidate_pool]]

        if not candidate_docs:
            return []

        # Step 4: FlashRank Cross-Encoder Re-ranking
        if self.reranker_enabled and self.ranker:
            try:
                passages = [
                    {"id": idx, "text": doc.page_content, "meta": doc.metadata}
                    for idx, doc in enumerate(candidate_docs)
                ]

                rerank_request = RerankRequest(query=query, passages=passages)
                reranked_results = self.ranker.rerank(rerank_request)

                # Format top_k reranked results
                final_results = []
                for item in reranked_results[:top_k]:
                    final_results.append({
                        "content": item["text"],
                        "metadata": item["meta"],
                        "score": round(float(item["score"]), 4),
                        "retrieval_method": "hybrid_flashrank",
                    })
                return final_results

            except Exception as e:
                logger.warning(f"[HybridSearch] FlashRank reranking error ({e}), returning RRF top-k.")

        # Fallback if reranker disabled
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": round(score, 4),
                "retrieval_method": "rrf_fused",
            }
            for doc, score in fused_candidates[:top_k]
        ]
