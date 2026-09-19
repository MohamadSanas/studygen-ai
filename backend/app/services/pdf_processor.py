from typing import List, Optional
from pathlib import Path
import re

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class PDFProcessor:
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ):
        # Hierarchical separators keep headings and paragraphs intact
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
            length_function=len,
            is_separator_regex=False,
        )

    def extract_text_and_split(
        self,
        file_path: str | Path,
        document_id: str,
        filename: Optional[str] = None,
    ) -> List[Document]:
        """
        Extracts text per page from PDF, splits into structure-aware chunks,
        and enriches with positional metadata.
        """
        reader = PdfReader(str(file_path))
        raw_documents: List[Document] = []
        doc_title = filename or Path(file_path).name

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            # Clean non-standard whitespace while keeping structure
            cleaned_text = re.sub(r"[ \t]+", " ", text).strip()

            if not cleaned_text:
                continue

            raw_documents.append(
                Document(
                    page_content=cleaned_text,
                    metadata={
                        "document_id": document_id,
                        "document_title": doc_title,
                        "page": page_number,
                    },
                )
            )

        # Split documents using hierarchical separators
        chunks = self.text_splitter.split_documents(raw_documents)

        # Enrich chunk metadata and add contextual location prefix
        enriched_chunks: List[Document] = []
        for chunk_index, chunk in enumerate(chunks):
            page_num = chunk.metadata.get("page", 1)
            content = chunk.page_content.strip()

            # Prepend context header for better retrieval representation
            contextualized_content = f"[Document: {doc_title} | Page {page_num}]\n{content}"

            enriched_chunks.append(
                Document(
                    page_content=contextualized_content,
                    metadata={
                        **chunk.metadata,
                        "chunk_index": chunk_index,
                        "char_count": len(content),
                        "word_count": len(content.split()),
                        "raw_content": content,
                    },
                )
            )

        return enriched_chunks
