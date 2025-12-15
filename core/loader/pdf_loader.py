import io
from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader

class PdfLoader:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    async def docs_from_pdf_bytes(self, pdf_bytes: bytes, source_name: str | int) -> List[Document]:
        reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
        docs: List[Document] = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                continue
            
            chunks = self.text_splitter.split_text(text)
            
            for chunk_idx, chunk in enumerate(chunks):
                docs.append(Document(
                    page_content=chunk,
                    metadata={
                        "text": chunk,
                        "page": page_num,
                        "chunk": chunk_idx,
                        "source": source_name
                    }
                ))
        return docs