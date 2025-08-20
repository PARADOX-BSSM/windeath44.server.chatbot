import io
from typing import List
from langchain_core.documents import Document
from pypdf import PdfReader

class PdfLoader:

    async def docs_from_pdf_bytes(self, pdf_bytes: bytes, source_name: str | int) -> List[Document]:
        reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
        docs: List[Document] = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                continue
            docs.append(Document(
                page_content=text,
                metadata={
                    "text" : text,
                    "page": page_num,
                    "source": source_name
                }
            ))
        return docs
