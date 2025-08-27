from fastapi import APIRouter, Depends
from api.schemas.common.request.cursor_query import CursorQuery
from api.schemas.common.response.base_response import BaseResponse
from api.schemas.request.chatbot_wordset_request import ChatBotWordSetRequest, ChatBotWordIdsRequest
from services import chatbot_wordset_service
from api.depends.get_user_id import get_user_id

router = APIRouter(prefix="/chatbots-wordset", tags=["chatbot_wordset"])

@router.post("/{character_id}")
async def chatbot_wordset(character_id : int, chatbot_wordset_request: ChatBotWordIdsRequest, user_id : str = Depends(get_user_id)) -> BaseResponse:
    await chatbot_wordset_service.add(character_id, chatbot_wordset_request, user_id)
    return BaseResponse(message="chatbot wordset successfully add")

@router.get("/")
async def get_chatbot_wordset(params : CursorQuery = Depends()) -> BaseResponse:
    chatbot_response = await chatbot_wordset_service.get_chatbot_wordset(params.cursor_id, params.size)
    return BaseResponse(message="chatbot wordset successfully get", data=chatbot_response)

@router.get("/{character_id}")
async def get_chatbot_wordset_by_character(character_id : int, params : CursorQuery = Depends()) -> BaseResponse:
    chatbot_response = await chatbot_wordset_service.get_chatbot_wordset_by_character(character_id, params.cursor_id, params.size)
    return BaseResponse(message="chatbot wordset successfully get by character", data=chatbot_response)

