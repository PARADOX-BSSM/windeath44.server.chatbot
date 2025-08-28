from fastapi import APIRouter, Depends, Query

from core.grpcs.client.chatbot_grpc_client import ChatbotGrpcClient
from api.depends.get_user_id import get_user_id
from api.schemas.common.request.cursor_query import CursorQuery
from api.schemas.common.response.base_response import BaseResponse
from api.schemas.request.chatbot_request import ChatRequest, ChatBotWordSetIdsRequest, ChatBotGenerateRequest
from app.chatbot.service import chatbot_service
from core.grpcs.deps.chatbot_stub_dep import chatbot_stub_dep

router = APIRouter(prefix="/chatbots", tags=["chatbot"])

# 캐릭터 챗
@router.post("/chat/{chatbot_id}")
async def chat(
        chatbot_id: int,
        chat_request : ChatRequest,
        user_id : str = Depends(get_user_id),
    ) -> BaseResponse:
    chatbot_response = await chatbot_service.chat(chatbot_id, chat_request, user_id)
    return BaseResponse(message="chatbot successfully answered", data=chatbot_response)

# 캐릭터 챗봇 생성
@router.post("/generate/{character_id}")
async def generate(
        character_id : int,
        chatbot_generate_request : ChatBotGenerateRequest,
        chatbot_grpc_client : ChatbotGrpcClient = Depends(chatbot_stub_dep
    )
) -> BaseResponse:
    await chatbot_service.generate(character_id, chatbot_generate_request, chatbot_grpc_client)
    return BaseResponse(message="chatbot successfully generated")

# 챗봇 말투셋 추가(수정)
@router.patch("/{chatbot_id}/wordset")
async def modify_wordsets(chatbot_id : int, chatbot_request : ChatBotWordSetIdsRequest) -> BaseResponse:
    await chatbot_service.modify(chatbot_id, chatbot_request.chatbot_wordset_ids)
    return BaseResponse(message="successfully added wordset")

@router.get("/{chatbot_id}")
async def get_chat(chatbot_id: int) -> BaseResponse:
    chatbot_response = await chatbot_service.get_chatbot(chatbot_id)
    return BaseResponse(message="chatbot successfully retrieved", data=chatbot_response)

# 챗봇 리스트 조회
@router.get("/")
async def list_chatbots(
        params : CursorQuery = Depends(),
        is_open : bool = Query(True, alias="isOpen"),
) -> BaseResponse:
    cursor_response = await chatbot_service.find_by_pagenate(is_open, params.cursor_id, params.size)
    return BaseResponse(message="chatbot successfully get", data=cursor_response)

# 챗봇 is_open 필드 토글 수정
@router.patch("/{chatbot_id}/open")
async def open_chatbot(chatbot_id : int) -> BaseResponse:
    is_open = await chatbot_service.toggle_open(chatbot_id)
    return BaseResponse(message="chatbot successfully opened" if is_open else "chatbot successfully closed")
