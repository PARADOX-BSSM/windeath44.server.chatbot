from typing import List

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from core.vectorstores.pinecone_vectorstore import PineconeVectorStore
from core.embedder.embedder import Embedder
from app.chatbot.exception.upsert_pinecone_failed_exception import UpsertPineconeFailedException


class CharacterVectorStore(PineconeVectorStore):
    def __init__(self, character_name : str = None, character_id : int = None):
        self.character_name = character_name
        self.character_id = character_id
        super().__init__(namespace=str(self.character_id))

    # override
    async def upsert(self, docs : List[Document], embed_model : Embedder):
        try:
            await super().upsert_documents(docs=docs, embed_model=embed_model)
            return True
        except Exception as e:
            print(str(e))
            raise UpsertPineconeFailedException(self.character_name)

    async def delete(self, embed_model : Embedder):
        self._init_vectorstore(embedder=embed_model)
        self.vectorstore.delete(delete_all=True, namespace=self.namespace)

    # 말투 넣을거임
    def retriever(self, embed_model: Embedder, top_k : int = 5, search_type : str = "mmr") -> VectorStoreRetriever:
        self._init_vectorstore(embedder=embed_model)
        retriever = self.vectorstore.as_retriever(
            # search_type
            # similarity
            # mmr
            search_type=search_type,
            search_kwargs={
                "k": top_k,
                "filter": {"source": {"$eq": self.character_id}}
            },
        )
        return retriever
