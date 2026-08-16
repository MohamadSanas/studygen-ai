from pathlib import Path

from app.services.pdf_processor import PDFProcessor


def main():
    pdf_processor = PDFProcessor()

    pdf_path = Path(
        "C:/Users/sanas/Desktop/my learn/Projects/"
        "studygen-ai/backend/test_data/Charles_s_CV_Template (5).pdf"
    )

    if not pdf_path.exists():
        print("PDF not found:", pdf_path)
        return

    print("PDF found")

    docs = pdf_processor.extract_text_and_split(
        pdf_path,
        "doc-123"
    )

    print(f"Extracted {len(docs)} chunks.\n")

    for i, doc in enumerate(docs):
        print("=" * 80)
        print(f"Chunk: {i}")
        print(f"Metadata: {doc.metadata}")
        print(f"Text:\n{doc.page_content[:500]}")
        print()


if __name__ == "__main__":
    main()