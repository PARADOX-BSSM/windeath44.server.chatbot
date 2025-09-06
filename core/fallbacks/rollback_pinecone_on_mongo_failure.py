from contextlib import asynccontextmanager

from core.embedder.embedder import Embedder
from app.chatbot.repository.character_vector_store import CharacterVectorStore

@asynccontextmanager
async def rollback_pinecone_on_mongo_failure(character_id : int, character_name : str):
    try:
        yield
    except Exception as e:
        print(e)
        character_vector_store = CharacterVectorStore(character_name=character_name, character_id=character_id)
        embedder = Embedder()
        await character_vector_store.delete(embedder)