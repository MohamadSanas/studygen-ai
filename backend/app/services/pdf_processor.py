import os
from typing import List
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pathlib import Path

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def extract_text_and_split(self, file_path: str, document_id: str) -> List[Document]:
        reader = PdfReader(file_path)
        raw_docs = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                raw_docs.append(
                    Document(
                        page_content=text,
                        metadata={
                            "document_id": document_id,
                            "page": i + 1,
                        }
                    )
                )
        chunks = self.text_splitter.split_documents(raw_docs)

        for index,chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = index

        return chunks


# Test PDF Processor
if __name__ == "__main__":
    processor = PDFProcessor()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, "Charles_s_CV_Template (5).pdf")
    docs = processor.extract_text_and_split(pdf_path, "doc-123")
    for doc in docs:
        print(doc)

    print(f"Extracted {len(docs)} chunks.")
    