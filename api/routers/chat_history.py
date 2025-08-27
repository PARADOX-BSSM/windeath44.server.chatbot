from fastapi import APIRouter, Depends

from api.depends.get_user_id import get_user_id
from api.schemas.common.response.base_response import BaseResponse
from api.schemas.common.request.cursor_query import CursorQuery
from services import chat_hisotry_service

router = APIRouter(prefix="/chat-history", tags=["chat-history"])

@router.get("/{chatbot_id}")
async def get_chat_history(chatbot_id : int, params : CursorQuery = Depends(), user_id : str = Depends(get_user_id)) -> BaseResponse:
    chat_history_response = await chat_hisotry_service.get_chat_histories(
        chatbot_id,
        params.cursor_id,
        params.size,
        user_id
    )
    return BaseResponse(message="chatbot chat history successfully get", data=chat_history_response)
