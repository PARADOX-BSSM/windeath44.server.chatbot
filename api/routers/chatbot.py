from fastapi import APIRouter, Depends

from api.schemas.common.request.cursor_query import CursorQuery
from api.schemas.common.response.base_response import BaseResponse
from api.schemas.request.chat_request import ChatRequest, ChatBotIdsRequest
from api.schemas.request.chatbot_wordset_request import ChatBotWordSetRequest
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

# 챗봇 말투셋 추가(수정)
@router.patch("/{chatbot_id}")
async def modify_wordsets(chatbot_id : int, chatbot_request : ChatBotIdsRequest) -> BaseResponse:
    await chatbot_service.modify(chatbot_id, chatbot_request.chatbot_ids)
    return BaseResponse(message="successfully added wordset")

# 챗봇 리스트 조회
@router.get("/")
async def list_chatbots(
        params : CursorQuery = Depends(),
) -> BaseResponse:
    cursor_response = await chatbot_service.find_by_pagenate(params.cursor_id, params.size)
    return BaseResponse(message="chatbot successfully get", data=cursor_response)