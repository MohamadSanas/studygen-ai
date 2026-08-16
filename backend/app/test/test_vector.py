from pathlib import Path

from app.services.pdf_processor import PDFProcessor
from app.services.vector_service import VectorService


def main():

    # -------------------------
    # 1. Process PDF
    # -------------------------

    pdf_processor = PDFProcessor()

    base_dir = Path(__file__).resolve().parents[2]

    pdf_path = (
        base_dir
        / "test_data"
        / "Charles_s_CV_Template (5).pdf"
    )

    if not pdf_path.exists():
        print("PDF not found:", pdf_path)
        return

    documents = pdf_processor.extract_text_and_split(
        str(pdf_path),
        "doc-123"
    )

    print(f"Extracted {len(documents)} chunks")


    # -------------------------
    # 2. Store in ChromaDB
    # -------------------------

    vector_service = VectorService()

    vector_service.add_documents(documents)

    print("Documents added to ChromaDB")


    # -------------------------
    # 3. Semantic search
    # -------------------------

    query = "What skills does this person have?"

    results = vector_service.similarity_search(
        query,
        k=3
    )

    print("\nSearch results:\n")

    for i, doc in enumerate(results):

        print("=" * 80)

        print(f"Result {i + 1}")

        print("Metadata:")
        print(doc.metadata)

        print("\nContent:")
        print(doc.page_content[:1000])


if __name__ == "__main__":
    main()