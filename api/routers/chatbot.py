from fastapi import APIRouter

from api.schemas.common.response.BaseResponse import BaseResponse
from api.schemas.request.chat_request import ChatRequest
from services import chatbot_service

router = APIRouter(prefix="/chatbots", tags=["chatbot"])

# 캐릭터 챗
@router.post("/chat/{chatbot_id}")
async def chat(
        chatbot_id: int,
        chat_request : ChatRequest
    ) -> BaseResponse:
    chatbot_response = await chatbot_service.chat(chatbot_id, chat_request)
    return BaseResponse(message="chatbot successfully answered", data=chatbot_response)

# 캐릭터 챗봇 생성
@router.post("/generate/{character_id}")
async def generate(
        character_id : int
) -> BaseResponse:
    await chatbot_service.generate(character_id)
    return BaseResponse(message="chatbot successfully generated")

