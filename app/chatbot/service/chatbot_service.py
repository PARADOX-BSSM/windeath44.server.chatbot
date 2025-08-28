import asyncio
from langchain_core.vectorstores import VectorStoreRetriever
from nadf.crawler import Crawler
from nadf.pdf import PDF
from langchain_core.documents import Document
from core.grpcs.client.chatbot_grpc_client import ChatbotGrpcClient
from api.schemas.common.response.cursor_response import CursorResponse
from api.schemas.request.chatbot_request import ChatRequest, ChatBotGenerateRequest
from api.schemas.response.chatbot_response import ChatResponse, ChatBotResponse
from app.chatbot.document.chatbot import ChatBot, CharacterWordSet
from app.chatbot.repository.character_vector_store import CharacterVectorStore
from core.embedder.embedder import Embedder
from core.loader.pdf_loader import PdfLoader
from typing import List, Tuple
from ai.character_chat_bot import CharacterChatBot
from app.chatbot_wordset.repository import chatbot_wordset_repo
from app.chatbot.repository import chatbot_repo
from app.chatbot.exception.already_exists_chatbot_exception import AlreadyExistsChatbotException
from core.fallbacks.rollback_pinecone_on_mongo_failure import rollback_pinecone_on_mongo_failure
from core.sessions import session_id_generator
from app.chatbot.mapper import chatbot_mapper


async def chat(chatbot_id : int, chat_request : ChatRequest, user_id : str) -> ChatResponse:
    chatbot = await _get_chatbot(chatbot_id)
    chatbot_name = chatbot.name

    mmr_retriever, similarity_retriever = await __get_retriever(chatbot_id, chatbot_name)

    session_id = await session_id_generator.generate_chat_session_id(chatbot_id=chatbot_id, user_id=user_id)

    chatbot = CharacterChatBot(character_name=chatbot_name, character_wordset=chatbot.character_wordset, session_id=session_id)
    await chatbot.build_chain(mmr_retriever=mmr_retriever, similarity_retriever=similarity_retriever)

    content = chat_request.content
    response = await chatbot.ainvoke(content)
    print(response)

    return ChatResponse(answer=response)


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




async def generate(character_id : int, chatbot_generate_request : ChatBotGenerateRequest, chatbot_grpc_client : ChatbotGrpcClient):
    print("check exsists ...")
    exists_chatbot = await chatbot_repo.exists_by_id(character_id)
    if exists_chatbot: raise AlreadyExistsChatbotException(character_id=character_id)

    print("generating chatbot ...")
    character = await chatbot_grpc_client.get_character(character_id)
    character_name = character.name

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
        await chatbot_repo.save(character_id=character_id, description=chatbot_generate_request.description, character_name=character_name)

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
    )
    return pdf_bytes


async def _crawl_namuwiki(character_name : str) -> List[Tuple[str, str, str]]:
    crawler = Crawler()
    namuwiki_list = await crawler.get_namuwiki_list(name=character_name)
    return namuwiki_list


async def _get_character_name_by_gRPC(character_id: int) -> str:
    character_name = "미야조노 카오리"  # 캐릭터 이름 DB에서 조회 (grpcs 이용 anime 서버랑 통신)
    return character_name


async def _upsert_character_document_for_pincone(character_id : int, character_name : str, documents : List[Document]):
    embedder = Embedder()
    character_pinecone_dao = CharacterVectorStore(
        character_name=character_name,
        character_id=character_id
    )
    # pinecone 저장
    await character_pinecone_dao.upsert(docs=documents, embed_model=embedder)

async def modify(character_id : int, chatbot_wordset_ids : List[str]):
    # chatbot
    character_wordsets = await chatbot_wordset_repo.find_chatbot_wordests(chatbot_wordset_ids)
    contributor = [wordset.writer_id for wordset in character_wordsets]

    chatbot_wordsets = [CharacterWordSet(question=character_wordset.question, answer=character_wordset.answer, contributor=character_wordset.writer_id) for character_wordset in character_wordsets]

    await chatbot_repo.update_wordset(character_id, chatbot_wordsets, contributor)


async def find_by_pagenate(is_open : bool, cursor_id : int, size : int) -> CursorResponse:
    chatbot_list = await chatbot_repo.find(is_open, size) if cursor_id is None else await chatbot_repo.find_by_cursor_id(is_open, cursor_id, size)
    chatbot_response = [await chatbot_mapper.to_chatbot_response(chatbot=chatbot) for chatbot in chatbot_list]

    has_next = len(chatbot_list) > size
    return CursorResponse(hasNext=has_next, values=chatbot_response[:size])

async def get_chatbot(chatbot_id : int) -> ChatBotResponse:
    chatbot = await chatbot_repo.find_by_id(chatbot_id)
    chatbot_response = await chatbot_mapper.to_chatbot_response(chatbot=chatbot)
    return chatbot_response
