from typing import Optional
from fastapi import APIRouter, Depends, Query
from api.schemas.common.request.cursor_query import CursorQuery
from api.schemas.common.response.base_response import BaseResponse
from api.schemas.request.chatbot_wordset_request import ChatBotWordIdsRequest
from app.chatbot_wordset.service import chatbot_wordset_service
from api.depends.get_user_id import get_user_id

router = APIRouter(prefix="/chatbots/wordset", tags=["character_wordset"])


# 말투셋 추가 요청
@router.post("/{character_id}")
async def chatbot_wordset(
    character_id: int, 
    chatbot_wordset_request: ChatBotWordIdsRequest, 
    user_id: str = Depends(get_user_id)
) -> BaseResponse:
    await chatbot_wordset_service.add(character_id, chatbot_wordset_request, user_id)
    return BaseResponse(message="chatbot wordset request successfully created")


# 어드민 - 말투셋 승인
@router.patch("/{wordset_id}/approve")
async def approve_wordset(wordset_id: str) -> BaseResponse:
    await chatbot_wordset_service.approve_wordset(wordset_id)
    return BaseResponse(message="chatbot wordset successfully approved")


# 어드민 - 말투셋 거절
@router.patch("/{wordset_id}/reject")
async def reject_wordset(wordset_id: str) -> BaseResponse:
    await chatbot_wordset_service.reject_wordset(wordset_id)
    return BaseResponse(message="chatbot wordset successfully rejected")



# 말투셋 삭제
@router.delete("/{wordset_id}")
async def delete_wordset(wordset_id: str) -> BaseResponse:
    await chatbot_wordset_service.delete_wordset(wordset_id)
    return BaseResponse(message="chatbot wordset successfully deleted")

# 캐릭터별 말투셋 조회 (상태별 필터링 가능)
@router.get("/{character_id}")
async def get_chatbot_wordset_by_character(
    character_id: int, 
    params: CursorQuery = Depends(),
    status: Optional[str] = Query(None, description="PENDING, APPROVED, REJECTED")
) -> BaseResponse:
    chatbot_response = await chatbot_wordset_service.get_chatbot_wordset_by_character_with_status(
        character_id, params.cursor_id, params.size, status
    )
    return BaseResponse(message="chatbot wordset successfully retrieved by character", data=chatbot_response)

