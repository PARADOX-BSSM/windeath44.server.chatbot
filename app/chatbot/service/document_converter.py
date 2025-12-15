from typing import List, Tuple
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentConverter:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    async def convert_namuwiki_to_documents(
        self, 
        character_id: int, 
        namuwiki_list: List[Tuple[str, str, str]]
    ) -> List[Document]:
        documents = []
        
        for section_idx, (title, content, level) in enumerate(namuwiki_list):
            # 제목과 내용을 결합하여 컨텍스트 유지
            full_text = f"# {title}\n\n{content}" if title else content
            
            if not full_text.strip():
                continue
            
            # 텍스트를 청크로 분할
            chunks = self.text_splitter.split_text(full_text)
            
            for chunk_idx, chunk in enumerate(chunks):
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "text": chunk,
                        "section": title,
                        "section_index": section_idx,
                        "chunk": chunk_idx,
                        "level": level,
                        "source": character_id
                    }
                ))
        
        return documents

document_converter = DocumentConverter(chunk_size=500, chunk_overlap=150)
