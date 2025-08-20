import asyncio

from nadf.crawler import Crawler
from nadf.pdf import PDF
from langchain_core.documents import Document

from api.v1.dto.chat_request import ChatRequest
from dao.pinecone.character_dao import CharacterDAO
from embedder.embedder import Embedder
from loader.pdf_loader import PdfLoader
from typing import List

from model.character_chat_bot import CharacterChatBot


async def generate(character_id : int) -> bool:
    print("generating chatbot ...")

    character_name = "호시노 아이" #  캐릭터 이름 DB에서 조회 (gRPC 이용 anime 서버랑 통신)

    print("crawling  ...")
    crawler = Crawler()
    namuwiki_list : List[(str, str, str)]= await crawler.get_namuwiki_list(name=character_name)
    # title, content, level을 튜플의 요소로 갖고 있음.

    print("generating pdf ...")
    doc_title = f"{character_name} 세계관"
    pdf = PDF(doc_title=doc_title)

    output_path = "./"
    pdf_bytes = await pdf.create_pdf_from_namuwiki_list(namuwiki_list=namuwiki_list, output_path=output_path, return_type=PDF.ReturnType.SAVE)
    pdfLoader = PdfLoader()
    documents : List[Document] = await pdfLoader.docs_from_pdf_bytes(pdf_bytes=pdf_bytes, source_name=character_id)

    print("saveing document for pinecone ...")
    embedder = Embedder()
    character_pinecone_dao = CharacterDAO(
        character_name=character_name,
        character_id=character_id
    )

    # pinecone 저장
    await character_pinecone_dao.upsert(docs=documents, embed_model=embedder)

    print("success ...")
    return False


async def chat(character_id : int, chat_request : ChatRequest):
    # character 이름 조회
    character_name = "호시노 아이"
    character_pinecone_dao = CharacterDAO(
        character_id=character_id,
        character_name=character_name
    )

    embedder = Embedder()
    retriever = character_pinecone_dao.retriever(embed_model=embedder, top_k=10)
    chatbot = CharacterChatBot(character_name=character_name)
    chatbot.build_chain(retriever=retriever)
    content = chat_request.content
    response = await chatbot.ainvoke(content)
    print(response)
    return None


if __name__ == "__main__":
    asyncio.run(generate(character_id=1))

    # content="왜 죽었어?"
    # asyncio.run(chat(character_id=1, chat_request=ChatRequest(content=content)))

    pass