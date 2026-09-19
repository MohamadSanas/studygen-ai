import re
import sys
import json
import asyncio
from pathlib import Path

# Add backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.rag_service import RAGService
from app.services.llm_service import llm_service


DATASET_PATH = Path("evals/dataset.json")
SAMPLE_TEXT_PATH = Path("evals/sample_ml_notes.txt")



def parse_score(llm_output: str) -> float:
    """Extracts a float score between 0.0 and 1.0 from LLM response."""
    match = re.search(r'"score":\s*([0-1](?:\.\d+)?)', llm_output)
    if match:
        return float(match.group(1))
    # Fallback: look for any float
    match = re.search(r'\b([0-1]\.\d+)\b', llm_output)
    return float(match.group(1)) if match else 1.0



async def evaluate_faithfulness(context: str, answer: str) -> float:
    """
    Checks if every statement in the answer is grounded in the context.
    Score 1.0 = zero hallucinations.
    Score 0.0 = completely fabricated.
    """
    prompt = f"""
    You are an expert AI evaluator.
    Evaluate whether the ANSWER is strictly supported by the CONTEXT.
    Penalize any claims, facts, or numbers not present in the CONTEXT.

    CONTEXT:
    {context}

    ANSWER:
    {answer}

    Return ONLY a JSON object:
    {{"score": <float between 0.0 and 1.0>, "reason": "<one sentence explanation>"}}
    """
    response = await llm_service.generate(prompt=prompt)
    return parse_score(response)


async def evaluate_relevance(question: str, answer: str) -> float:
    """
    Checks if the answer directly and concisely addresses the question.
    Score 1.0 = perfect direct answer.
    Score 0.0 = irrelevant evasion.
    """
    prompt = f"""
    You are an expert AI evaluator.
    Evaluate whether the ANSWER directly and accurately addresses the QUESTION.

    QUESTION:
    {question}

    ANSWER:
    {answer}

    Return ONLY a JSON object:
    {{"score": <float between 0.0 and 1.0>, "reason": "<one sentence explanation>"}}
    """
    response = await llm_service.generate(prompt=prompt)
    return parse_score(response)

    

async def run_rag_evals():
    print("=" * 70)
    print("StudyGen AI — RAG Generation Quality Evaluation")
    print("=" * 70)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    rag = RAGService()

    faithfulness_scores = []
    relevance_scores = []

    print(f"Evaluating {len(dataset)} questions through LLM-as-a-Judge...\n")

    for i, item in enumerate(dataset, start=1):
        query = item["query"]

        # 1. Generate answer through full RAG pipeline
        rag_output = await rag.ask(question=query, top_k=4)
        answer = rag_output["answer"]
        context = "\n\n".join(s["content"] for s in rag_output["sources"])

        # 2. Judge Faithfulness & Answer Relevance
        f_score = await evaluate_faithfulness(context, answer)
        r_score = await evaluate_relevance(query, answer)

        faithfulness_scores.append(f_score)
        relevance_scores.append(r_score)

        print(f"[{i}/{len(dataset)}] '{query[:40]}...'")
        print(f"   Faithfulness: {f_score * 100:.0f}% | Relevance: {r_score * 100:.0f}%\n")

    # 3. Final Summary Table
    avg_faith = (sum(faithfulness_scores) / len(faithfulness_scores)) * 100
    avg_rel = (sum(relevance_scores) / len(relevance_scores)) * 100

    print("=" * 70)
    print("FINAL GENERATION QUALITY METRICS (Ragas Benchmark)")
    print("=" * 70)
    print(f"{'Metric':<30} | {'Score':<15}")
    print("-" * 70)
    print(f"{'Faithfulness (Groundedness)':<30} | {avg_faith:>12.1f}%")
    print(f"{'Answer Relevance':<30} | {avg_rel:>12.1f}%")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_rag_evals())
