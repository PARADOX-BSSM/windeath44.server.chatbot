import asyncio
from langchain_core.vectorstores import VectorStoreRetriever
from nadf.crawler import Crawler
from nadf.pdf import PDF
from langchain_core.documents import Document
from api.schemas.request.chat_request import ChatRequest
from api.schemas.response.chatbot_response import ChatbotResponse
from domain.documents.chatbot import ChatBot
from domain.repositories.character_vector_store import CharacterVectorStore
from adapter.embedder.embedder import Embedder
from adapter.loader.pdf_loader import PdfLoader
from typing import List, Tuple
from ai.character_chat_bot import CharacterChatBot
from domain.repositories import chatbot_repo
from exceptions.already_exists_chatbot_exception import AlreadyExistsChatbotException
from fallbacks.rollback_pinecone_on_mongo_failure import rollback_pinecone_on_mongo_failure


async def chat(chatbot_id : int, chat_request : ChatRequest) -> ChatbotResponse:
    chatbot = await _get_chatbot(chatbot_id)
    chatbot_name = chatbot.name

    mmr_retriever, similarity_retriever = await __get_retriever(chatbot_id, chatbot_name)

    chatbot = CharacterChatBot(character_name=chatbot_name, character_wordset=chatbot.character_wordset)
    chatbot.build_chain(mmr_retriever=mmr_retriever, similarity_retriever=similarity_retriever)
    content = chat_request.content

    response = await chatbot.ainvoke(content)
    print(response)

    return ChatbotResponse(comment=response)


async def _get_chatbot(chatbot_id: int) -> ChatBot:
    chatbot = await chatbot_repo.find_by_id(chatbot_id)
    return chatbot


async def __get_retriever(character_id : int, character_name : str) -> Tuple[VectorStoreRetriever, VectorStoreRetriever]:
    character_pinecone_dao = CharacterVectorStore(
        character_id=character_id,
        character_name=character_name
    )
    embedder = Embedder()
    mmr_retriever = character_pinecone_dao.retriever(embed_model=embedder, top_k=5, search_type="mmr")
    similarity_retriever = character_pinecone_dao.retriever(embed_model=embedder, top_k=5, search_type="similarity")
    return mmr_retriever, similarity_retriever




async def generate(character_id : int):
    print("check exsists ...")
    exists_chatbot = await chatbot_repo.exists_by_id(character_id)
    if exists_chatbot: raise AlreadyExistsChatbotException(character_id=character_id)

    print("generating chatbot ...")
    character_name = await _get_character_name_by_gRPC(character_id)

    print("crawling  ...")
    namuwiki_list = await _crawl_namuwiki(character_name)
    # title, content, level을 튜플의 요소로 갖고 있음.

    print("generating pdf ...")
    pdf_bytes = await _generate_pdf(character_name, namuwiki_list)

    print("convert pdf to langchain's documents ...")
    documents = await _load_documents_from_pdf(character_id, pdf_bytes)

    print("saving document for pinecone ...")
    await _upsert_character_document_for_pincone(character_id, character_name, documents)

    print("saving character for mongodb ...")
    async with rollback_pinecone_on_mongo_failure(character_id=character_id, character_name=character_name):
        await chatbot_repo.save(character_id=character_id, character_name=character_name)

    print("success!!!")


async def _load_documents_from_pdf(character_id : int, pdf_bytes : bytes) -> List[Document]:
    pdfLoader = PdfLoader()
    documents = await pdfLoader.docs_from_pdf_bytes(pdf_bytes=pdf_bytes, source_name=character_id)
    return documents


async def _generate_pdf(character_name : str, namuwiki_list : List[Tuple[str, str, str]]):
    doc_title = f"{character_name} 세계관"
    pdf = PDF(doc_title=doc_title)
    pdf_bytes = await pdf.create_pdf_from_namuwiki_list(
        namuwiki_list=namuwiki_list,
        return_type=PDF.ReturnType.RETURN_BYTES,
        output_path="./"
    )
    return pdf_bytes


async def _crawl_namuwiki(character_name : str) -> List[Tuple[str, str, str]]:
    crawler = Crawler()
    namuwiki_list = await crawler.get_namuwiki_list(name=character_name)
    return namuwiki_list


async def _get_character_name_by_gRPC(character_id: int) -> str:
    character_name = "미야조노 카오리"  # 캐릭터 이름 DB에서 조회 (gRPC 이용 anime 서버랑 통신)
    return character_name


async def _upsert_character_document_for_pincone(character_id : int, character_name : str, documents : List[Document]):
    embedder = Embedder()
    character_pinecone_dao = CharacterVectorStore(
        character_name=character_name,
        character_id=character_id
    )
    # pinecone 저장
    await character_pinecone_dao.upsert(docs=documents, embed_model=embedder)

if __name__ == "__main__":
    # asyncio.run(generate(character_id=5))

    content="안졸려? 자고싶어 미치겠어"
    asyncio.run(chat(chatbot_id=1, chat_request=ChatRequest(content=content)))

    pass
