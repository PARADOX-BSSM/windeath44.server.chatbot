from fastapi import APIRouter

from api.common.dto.response.BaseResponse import BaseResponse
from api.v1.dto.request.chat_request import ChatRequest
from decorator.exception_handler import exception_handler
from service import chatbot_service

router = APIRouter(prefix="/chatbots", tags=["chatbot"])

# 캐릭터 챗
@exception_handler
@router.post("/chat/{character_id}")
async def chat(
        character_id: int,
        chat_request : ChatRequest
    ) -> BaseResponse:
    chatbot_response = await chatbot_service.chat(character_id, chat_request)
    return BaseResponse(message="chatbot successfully answered", data=chatbot_response)

# 캐릭터 챗봇 생성
@exception_handler
@router.post("/generate/{character_id}")
async def generate(
        character_id : int
) -> BaseResponse:
    chatbot_response = await chatbot_service.generate(character_id)
    return BaseResponse(message="chatbot successfully generated", data=chatbot_response)

