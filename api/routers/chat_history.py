from fastapi import APIRouter, Depends

from api.depends.get_user_id import get_user_id
from api.schemas.common.response.base_response import BaseResponse
from api.schemas.common.request.cursor_query import CursorQuery
from services import chat_hisotry_service

router = APIRouter(prefix="/chatbots/history", tags=["chat-history"])

# 대화 내역 가져오기
@router.get("/{chatbot_id}")
async def get_chat_history(chatbot_id : int, params : CursorQuery = Depends(), user_id : str = Depends(get_user_id)) -> BaseResponse:
    chat_history_response = await chat_hisotry_service.get_chat_histories(
        chatbot_id,
        params.cursor_id,
        params.size,
        user_id
    )
    return BaseResponse(message="chatbot chat history successfully get", data=chat_history_response)

# 세션 내 대화 내역 전체 삭제
@router.delete("/{chatbot_id}")
async def delete_session_history(chatbot_id : int, user_id : str = Depends(get_user_id)) -> BaseResponse:
    await chat_hisotry_service.delete_by_session_id(chatbot_id, user_id)
    return BaseResponse(message="chatbot chat session history successfully deleted")

# 대화 내역 단일 삭제
@router.delete("/{history_id}")
async def delete_history_by_id(history_id : str) -> BaseResponse:
    await chat_hisotry_service.delete_by_history_id(history_id)
    return BaseResponse(message="chatbot chat history successfully deleted")