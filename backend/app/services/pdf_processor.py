from typing import List
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class PDFProcessor:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def extract_text_and_split(
        self,
        file_path: str | Path,
        document_id: str,
    ) -> List[Document]:

        reader = PdfReader(file_path)

        raw_documents: List[Document] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if not text.strip():
                continue

            raw_documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "document_id": document_id,
                        "page": page_number,
                    },
                )
            )

        chunks = self.text_splitter.split_documents(raw_documents)

        for chunk_index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = chunk_index

        return chunks

    def extract_pages(
        self,
        file_path: str | Path,
        document_id: str,
    ) -> List[Document]:

        reader = PdfReader(file_path)

        documents: List[Document] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if not text.strip():
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "document_id": document_id,
                        "page": page_number,
                    },
                )
            )

        return documents