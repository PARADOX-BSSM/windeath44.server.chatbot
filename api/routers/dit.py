from fastapi import APIRouter, Depends
import random
from app.dit.service import dit_service
from api.schemas.common.response.base_response import BaseResponse
from core.grpcs.client.chatbot_grpc_client import ChatbotGrpcClient
from core.grpcs.deps.chatbot_stub_dep import chatbot_stub_dep
from app.chatbot.repository import chatbot_repo
from app.chatbot.exception.no_available_chatbot_exception import NoAvailableChatbotException
from app.dit.util.memorial_http_util import get_memorials_by_comment_count

router = APIRouter(prefix="/chatbots/dits", tags=["dit"])

@router.post("")
async def write_tribute(
        chatbot_grpc_client : ChatbotGrpcClient = Depends(chatbot_stub_dep)
):
    # 랜덤 chatbot 조회
    random_chatbot = await chatbot_repo.find_random(is_open=True)
    if not random_chatbot:
        raise NoAvailableChatbotException()

    character_id = random_chatbot.id

    # 댓글 수가 적은 memorial 10개 조회 후 랜덤 선택
    memorials = await get_memorials_by_comment_count(size=10)
    if not memorials:
        raise NoAvailableChatbotException()

    memorial_id = random.choice(memorials)["memorialId"]

    comment_response = await dit_service.write_memorial(character_id, memorial_id, chatbot_grpc_client)
    return BaseResponse(message="Tribute successfully written", data=comment_response)