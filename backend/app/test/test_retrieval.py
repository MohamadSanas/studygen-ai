from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStoreService


def main():

    pdf_processor = PDFProcessor()

    vector_store = VectorStoreService()

    # --------------------------------------------------
    # 1. Extract and chunk PDF
    # --------------------------------------------------

    documents = pdf_processor.extract_text_and_split(
        "test_data/ProcessLectureSlide.pdf",
        "ProcessLectureSlide",
    )

    print(f"Chunks created: {len(documents)}")

    # --------------------------------------------------
    # 2. Store chunks in ChromaDB
    # --------------------------------------------------

    vector_store.add_documents(documents)

    print("Documents added to ChromaDB")
    print(f"Total documents: {vector_store.vector_db._collection.count()}")

    # --------------------------------------------------
    # 3. Ask a question
    # --------------------------------------------------

    query = "What is a process?"

    print("\n" + "=" * 80)
    print("QUERY:")
    print(query)
    print("=" * 80)

    results = vector_store.similarity_search(
        query=query,
        document_id="ProcessLectureSlide",
        k=4,
    )

    # --------------------------------------------------
    # 4. Display retrieved chunks
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("RETRIEVED DOCUMENTS")
    print("=" * 80)

    for i, document in enumerate(results, start=1):

        print(f"\n--- RESULT {i} ---")

        print("Metadata:")
        print(document.metadata)

        print("\nContent:")
        print(document.page_content)

        print("--- END RESULT ---")


if __name__ == "__main__":
    main()