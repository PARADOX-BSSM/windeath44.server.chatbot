from dotenv import load_dotenv
from langchain_core.vectorstores import VectorStoreRetriever
from app.chatbot.service.document_converter import document_converter
from app.chatbot.service.namuwiki_crawler_service import namuwiki_crawler_service
from app.chatbot.service.vector_store_service import vector_store_service
from core.grpcs.client import UserGrpcClient
from core.grpcs.client.chatbot_grpc_client import ChatbotGrpcClient
from api.schemas.common.response.cursor_response import CursorResponse
from api.schemas.request.chatbot_request import ChatRequest, ChatBotGenerateRequest
from api.schemas.response.chatbot_response import ChatResponse, ChatBotResponse
from app.chatbot.document.chatbot import ChatBot, CharacterWordSet
from app.chatbot.repository.character_vector_store import CharacterVectorStore
from core.embedder.embedder import Embedder
from typing import List, Tuple
from ai.character_chat_bot import CharacterChatBot
from app.chatbot_wordset.repository import chatbot_wordset_repo
from app.chatbot.repository import chatbot_repo
from app.chatbot.exception.already_exists_chatbot_exception import AlreadyExistsChatbotException
from app.chatbot.exception.insufficient_token_exception import InsufficientTokenException
from core.fallbacks.rollback_pinecone_on_mongo_failure import rollback_pinecone_on_mongo_failure
from core.sessions import session_id_generator
from app.chatbot.mapper import chatbot_mapper
from app.chatbot.event.chat_event_publisher import publish_chat_event
from core.events.event_publisher import EventPublisher
import time

load_dotenv()


async def chat(chatbot_id : int, chat_request : ChatRequest, user_id : str, user_grpc_client : UserGrpcClient, event_publisher: EventPublisher) -> ChatResponse:
    remain_token = await user_grpc_client.get_user_remain_token(user_id=user_id)

    content = chat_request.content

    chatbot = await _get_chatbot(chatbot_id)
    chatbot_name = chatbot.name

    mmr_retriever, similarity_retriever = await __get_retriever(chatbot_id, chatbot_name)
    session_id = await session_id_generator.generate_chat_session_id(chatbot_id=chatbot_id, user_id=user_id)

    chatbot_instance = CharacterChatBot(character_name=chatbot_name, character_wordset=chatbot.character_wordset, session_id=session_id)

    await chatbot_instance.build_chain(mmr_retriever=mmr_retriever, similarity_retriever=similarity_retriever)

    # 실행 전 토큰 사용량 예측
    estimated_tokens = await chatbot_instance.estimate_prompt_tokens(content)
    print(f"Estimated tokens: {estimated_tokens}, Remain tokens: {remain_token}")

    # 토큰 부족 체크
    if estimated_tokens > remain_token:
        raise InsufficientTokenException(
            required_tokens=estimated_tokens,
            remain_tokens=remain_token
        )

    # 채팅 실행 및 토큰 사용량 측정 (시간 측정)
    start_time = time.time()
    result = await chatbot_instance.ainvoke(content)
    response_time_ms = int((time.time() - start_time) * 1000)
    
    answer = result["answer"]
    token_usage = result.get("token_usage", {})
    
    print(f"Answer: {answer}")
    print(f"Token Usage: {token_usage}")
    print(f"  - prompt_tokens: {token_usage.get('prompt_tokens', 0)}")
    print(f"  - completion_tokens: {token_usage.get('completion_tokens', 0)}")
    print(f"  - total_tokens: {token_usage.get('total_tokens', 0)}")
    print(f"Response time: {response_time_ms}ms")
    
    # 채팅 이벤트를 Kafka에 발행
    await publish_chat_event(
        publisher=event_publisher,
        chatbot_id=chatbot_id,
        user_id=user_id,
        session_id=session_id,
        content=content,
        answer=answer,
        token_usage=token_usage,
        success=True,
        response_time_ms=response_time_ms,
        model_name=chatbot_instance.model_name,
    )

    return ChatResponse(answer=answer)


async def dit_chat(chatbot_id: int, chat_request: ChatRequest, user_id: str) -> ChatResponse:
    content = chat_request.content
    chatbot = await _get_chatbot(chatbot_id)
    chatbot_name = chatbot.name

    mmr_retriever, similarity_retriever = await __get_retriever(chatbot_id, chatbot_name)
    session_id = await session_id_generator.generate_chat_session_id(chatbot_id=chatbot_id, user_id=user_id)

    chatbot_instance = CharacterChatBot(
        character_name=chatbot_name,
        character_wordset=chatbot.character_wordset,
        session_id=session_id
    )

    await chatbot_instance.build_chain(mmr_retriever=mmr_retriever, similarity_retriever=similarity_retriever)

    estimated_tokens = await chatbot_instance.estimate_prompt_tokens(content)
    print(f"Estimated tokens: {estimated_tokens}")

    # 채팅 실행 및 토큰 사용량 측정 (시간 측정)
    start_time = time.time()
    result = await chatbot_instance.ainvoke(content)
    response_time_ms = int((time.time() - start_time) * 1000)

    answer = result["answer"]
    token_usage = result.get("token_usage", {})
    
    print(f"Answer: {answer}")
    print(f"Token Usage: {token_usage}")
    print(f"  - prompt_tokens: {token_usage.get('prompt_tokens', 0)}")
    print(f"  - completion_tokens: {token_usage.get('completion_tokens', 0)}")
    print(f"  - total_tokens: {token_usage.get('total_tokens', 0)}")
    print(f"Response time: {response_time_ms}ms")

    return ChatResponse(answer=answer)

async def find_chatbot(chatbot_id : int) -> ChatBot:
    chatbot = await _get_chatbot(chatbot_id)
    return chatbot

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

    print("crawling ...")
    namuwiki_list = await namuwiki_crawler_service.crawl_character(character_name)
    
    print("converting to documents ...")
    documents = await document_converter.convert_namuwiki_to_documents(character_id, namuwiki_list)
    
    print("saving documents to Pinecone ...")
    await vector_store_service.upsert_character_documents(character_id, character_name, documents)

    print("saving character for mongodb ...")
    async with rollback_pinecone_on_mongo_failure(character_id=character_id, character_name=character_name):
        await chatbot_repo.save(character_id=character_id, description=chatbot_generate_request.description, character_name=character_name)

    print("success!!!")

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
    chatbot_response = await chatbot_mapper.to_chatbot_details_response(chatbot=chatbot)
    return chatbot_response


async def toggle_open(chatbot_id : int) -> bool:
    is_open = await chatbot_repo.toggle_open(chatbot_id)
    return is_open
