from app.services.pdf_processor import PDFProcessor

processor = PDFProcessor()

pdf_path = "test_data/ProcessLectureSlide.pdf"

chunks = processor.extract_text_and_split(
    pdf_path,
    "lect_slide",
)

print(f"Total chunks: {len(chunks)}")

for chunk in chunks:
    print("\n" + "=" * 80)
    print("Metadata:", chunk.metadata)
    print("Content:")
    print(chunk.page_content)