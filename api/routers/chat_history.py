from fastapi import APIRouter, Depends

from api.schemas.common.response.base_response import BaseResponse
from api.schemas.common.request.cursor_query import CursorQuery
from services import chat_hisotry_service

router = APIRouter(prefix="/chat-history", tags=["chat-history"])


# @router.get("/{character_id}")
# async def get_chat_hisotry(character_id : int, params : CursorQuery = Depends()) -> BaseResponse:
#     chat_history_response = await chat_hisotry_service.get_chat_history()
#     return BaseResponse(message="", data=chat_history_response)