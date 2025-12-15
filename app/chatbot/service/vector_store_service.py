from typing import List
from langchain_core.documents import Document
from app.chatbot.repository.character_vector_store import CharacterVectorStore
from core.embedder.embedder import Embedder

class VectorStoreService:
    async def upsert_character_documents(
        self, 
        character_id: int, 
        character_name: str, 
        documents: List[Document]
    ) -> None:
        embedder = Embedder()
        character_vector_store = CharacterVectorStore(
            character_name=character_name,
            character_id=character_id
        )
        await character_vector_store.upsert(docs=documents, embed_model=embedder)
        print(f"Successfully upserted {len(documents)} documents to Pinecone for character '{character_name}'")

vector_store_service = VectorStoreService()
