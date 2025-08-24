import asyncio
import uuid
from typing import List, Dict

from dotenv import load_dotenv
import os

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone.db_data.types import VectorTypedDict

load_dotenv()

class Embedder:
    def __init__(self, model : str = "text-embedding-3-large"):
        self.emb = OpenAIEmbeddings(model=model, api_key=os.getenv("OPENAI_API_KEY"))

    async def load(self, character_name : str, docs : List[Document], chunk_size : int = 800, chunk_overlap : int = 120) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        docs = splitter.split_documents(docs)
        for d in docs:
            d.metadata.update({
                **d.metadata,
                "character": character_name,
            })
        return docs

    async def embed_documents(self, docs : List[Document]) -> List[VectorTypedDict]:
        vectors = []
        embeddings = await self.emb.aembed_documents([d.page_content for d in docs])
        for d, vec in zip(docs, embeddings):
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": vec,
                "metadata": d.metadata
            })
        return vectors

    async def embed_query(self, text : str):
        return self.emb.embed_query(text)

