from fastapi import APIRouter, Depends
from app.dit.service import dit_service
from api.schemas.common.response.base_response import BaseResponse
from core.grpcs.client.chatbot_grpc_client import ChatbotGrpcClient
from core.grpcs.deps.chatbot_stub_dep import chatbot_stub_dep
from app.chatbot.repository import chatbot_repo
from app.chatbot.exception.no_available_chatbot_exception import NoAvailableChatbotException

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

    # memorial id 랜덤이라 가정
    memorial_id = 1
    comment_response = await dit_service.write_memorial(character_id, memorial_id, chatbot_grpc_client)
    return BaseResponse(message="Tribute successfully written", data=comment_response)