from fastapi import APIRouter, Depends

from adapter.grpc.client.chatbot_grpc_client import ChatbotGrpcClient
from api.depends.get_user_id import get_user_id
from api.schemas.common.request.cursor_query import CursorQuery
from api.schemas.common.response.base_response import BaseResponse
from api.schemas.request.chat_request import ChatRequest, ChatBotWordSetIdsRequest
from services import chatbot_service
from adapter.grpc.deps.chatbot_stub_dep import chatbot_stub_dep

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
        chatbot_grpc_client : ChatbotGrpcClient = Depends(chatbot_stub_dep)
) -> BaseResponse:
    await chatbot_service.generate(character_id, chatbot_grpc_client)
    return BaseResponse(message="chatbot successfully generated")

# 챗봇 말투셋 추가(수정)
@router.patch("/{chatbot_id}")
async def modify_wordsets(chatbot_id : int, chatbot_request : ChatBotWordSetIdsRequest) -> BaseResponse:
    await chatbot_service.modify(chatbot_id, chatbot_request.chatbot_wordset_ids)
    return BaseResponse(message="successfully added wordset")

# 챗봇 리스트 조회
@router.get("/")
async def list_chatbots(
        params : CursorQuery = Depends(),
) -> BaseResponse:
    cursor_response = await chatbot_service.find_by_pagenate(params.cursor_id, params.size)
    return BaseResponse(message="chatbot successfully get", data=cursor_response)