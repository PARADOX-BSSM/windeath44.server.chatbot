import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from embedder.embedder import Embedder

load_dotenv()

class PineconeDAO:
    def __init__(self, namespace : str):
        self.namespace = namespace
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "paradox")
        self.index = pc.Index(self.index_name)
        self.vectorstore = None

    def _init_vectorstore(self, embedder: Embedder):
        self.vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            namespace=self.namespace,
            embedding=embedder.emb
        )


    # upload pinecone
    async def upsert_documents(self, docs: list, embed_model : Embedder):
        vectors = await embed_model.embed_documents(docs)  # 또는 embed_documents
        self.index.upsert(vectors=vectors, namespace=self.namespace)

    # search pinecone
    async def query(self, text: str, embed_model : Embedder, top_k: int = 5):
        vector = await embed_model.embed_query(text)
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=self.namespace,
            include_metadata=True
        )
        return results

    # delete all
    async def delete_all(self):
        self.index.delete(delete_all=True, namespace=self.namespace)

    # delete by ids
    async def delete_by_ids(self, ids: list):
        self.index.delete(ids=ids, namespace=self.namespace)

    async def stats(self):
        return self.index.describe_index_stats()

    def build_retriever(self, identity: str, embed_model: Embedder, top_k : int = 5):
        self._init_vectorstore(embedder=embed_model)
        retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": top_k,
                "filter": {"source": {"$eq": identity}}
            },
        )
        return retriever


