from fastapi import APIRouter

from api.v1.dto.chat_request import ChatRequest
from dao.pinecone.pinecone_dao import PineconeDAO
from decorator.exception_handler import exception_handler
from service import chatbot_service

router = APIRouter(prefix="/chatbots", tags=["chatbot"])

# 캐릭터 챗봇 생성
@exception_handler
@router.post("/{character_id}")
async def make_chatbot(character_id: int):
    result = await chatbot_service.generate(character_id)
    return result


@exception_handler
@router.post("/chat/{character_id}")
async def chat(
        character_id: int,
        chat_request : ChatRequest
    ):
    await chatbot_service.chat(character_id, chat_request)

