from fastapi import APIRouter
from app.dit.service import dit_service
from api.schemas.common.response.base_response import BaseResponse

router = APIRouter(prefix="/chatbots/dits", tags=["dit"])

@router.post("")
async def write_tribute():
    # character id 랜덤이라 가정
    # memorial id 랜덤이라 가정
    character_id = 1
    memorial_id = 103
    await dit_service.write_memorial(character_id, memorial_id)
    return BaseResponse(message="")