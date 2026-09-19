import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings
from app.services.hybrid_search import BM25Index, HybridSearchService


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DATASET_PATH = Path("evals/dataset.json")
SAMPLE_TEXT_PATH = Path("evals/sample_ml_notes.txt")
RESULTS_PATH = Path("evals/results.json")



def load_dataset(path: Path) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_sample_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def prepare_corpus(raw_text:str)->tuple[list[Document],Chroma]:
    splitter=RecursiveCharacterTextSplitter(chunk_size=600,chunk_overlap=100)
    docs = [Document(page_content=t,metadata={"source":"ml_notes"}) for t in splitter.split_text(raw_text)]
    model_name = settings.EMBEDDING_MODEL
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs={"normalize_embeddings": True}
    )

    vector_db = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="eval_benchmark",
        persist_directory="./evals/temp_chroma"
    )

    return docs, vector_db


def is_hit(chunk_text:str, expect_keywords:list[str])->bool:
    """
    Check if ANY of the expected keywords appear in the chunk.
    This defines a "hit" for our retrieval benchmark.
    """
    chunk_text_lower = chunk_text.lower()
    matches=0
    
    for keyword in expect_keywords:
        if keyword.lower() in chunk_text_lower:
            matches+=1
    return matches>= max(1,len(expect_keywords)*0.5)

def evaluate_retrieval(
    retrived_text:list[str],
    excepted_keyword:list[str],
    top_k:int=4)->tuple[float,float]:

    hits=0
    for rank,chunk in enumerate(retrived_text[:top_k],start=1):
        if is_hit(chunk,excepted_keyword):
            return 1,1/rank

    return 0,0
    

def run_benchmark():
    print("\nStarting Retrieval Benchmark...")
    start_time = time.time()
    dataset = load_dataset(DATASET_PATH)
    raw_text = load_sample_text(SAMPLE_TEXT_PATH)
    docs, vector_db = prepare_corpus(raw_text)
    
    bm25 = BM25Index(docs)
    hybrid_service = HybridSearchService()
    hybrid_service.vector_store.vector_db = vector_db

    metrics = {
        "Dense (Chroma)": {"hits": 0, "rr_sum": 0.0, "latencies": []},
        "Sparse (BM25)": {"hits": 0, "rr_sum": 0.0, "latencies": []},
        "Hybrid + FlashRank": {"hits": 0, "rr_sum": 0.0, "latencies": []},
    }
    

    print(f"Running benchmark across {len(dataset)} queries...\n")


    for i, item in enumerate(dataset, start=1):
        query = item["query"]
        expected = item["expected_keywords"]

        # 1. Test Dense Vector Search (ChromaDB)
        t0 = time.perf_counter()
        dense_results = vector_db.similarity_search(query, k=4)
        t_dense = (time.perf_counter() - t0) * 1000
        dense_texts = [doc.page_content for doc in dense_results]
        hit_d, rr_d = evaluate_retrieval(dense_texts, expected, top_k=4)
        metrics["Dense (Chroma)"]["hits"] += hit_d
        metrics["Dense (Chroma)"]["rr_sum"] += rr_d
        metrics["Dense (Chroma)"]["latencies"].append(t_dense)

        # 2. Test Sparse Keyword Search (BM25)
        t0 = time.perf_counter()
        bm25_results = bm25.search(query, top_k=4)
        t_bm25 = (time.perf_counter() - t0) * 1000
        bm25_texts = [doc.page_content for doc, _ in bm25_results]
        hit_b, rr_b = evaluate_retrieval(bm25_texts, expected, top_k=4)

        metrics["Sparse (BM25)"]["hits"] += hit_b
        metrics["Sparse (BM25)"]["rr_sum"] += rr_b
        metrics["Sparse (BM25)"]["latencies"].append(t_bm25)

        # 3. Test Hybrid Search + FlashRank Re-ranking
        t0 = time.perf_counter()
        hybrid_results = hybrid_service.search(query, top_k=4, candidate_pool=15)
        t_hybrid = (time.perf_counter() - t0) * 1000
        hybrid_texts = [c["content"] for c in hybrid_results]
        hit_h, rr_h = evaluate_retrieval(hybrid_texts, expected, top_k=4)
        
        metrics["Hybrid + FlashRank"]["hits"] += hit_h
        metrics["Hybrid + FlashRank"]["rr_sum"] += rr_h
        metrics["Hybrid + FlashRank"]["latencies"].append(t_hybrid)
        
        print(f"[{i}/{len(dataset)}] '{query[:40]}...'")
        
        print(f"   Dense: Hit={hit_d}, RR={rr_d:.2f} | BM25: Hit={hit_b}, RR={rr_b:.2f} | Hybrid: Hit={hit_h}, RR={rr_h:.2f}")
    # Display final aggregated results table
    n = len(dataset)
    print("\n" + "=" * 75)
    print("FINAL BENCHMARK COMPARISON (Top-4)")
    print("=" * 75)
    print(f"{'Strategy':<25} | {'Hit Rate@4':<12} | {'MRR':<8} | {'Avg Latency':<12}")
    print("-" * 75)


    for method, data in metrics.items():
        hit_rate = (data["hits"] / n) * 100
        mrr = data["rr_sum"] / n
        avg_lat = sum(data["latencies"]) / len(data["latencies"])
        print(f"{method:<25} | {hit_rate:>10.1f}% | {mrr:>8.3f} | {avg_lat:>10.2f} ms")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_benchmark()

    
    

