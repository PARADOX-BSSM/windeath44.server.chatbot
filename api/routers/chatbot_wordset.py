from fastapi import APIRouter

from api.schemas.common.response.BaseResponse import BaseResponse
from api.schemas.request.chatbot_wordset_request import ChatBotWordSetRequest
from services import chatbot_wordset_service

router = APIRouter(prefix="/chatbots/wordset", tags=["chatbot_wordset"])

@router.patch("/{character_id}")
async def modify_wordsets(character_id : int, chatbot_wordset_request : ChatBotWordSetRequest):
    await chatbot_wordset_service.modify(character_id, chatbot_wordset_request)
    return BaseResponse(message="successfully added wordset")

