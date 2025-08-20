from fastapi import APIRouter
from api.v1.endpoint.chatbot import router as chatbot_router

router = APIRouter(prefix="/v1")
router.include_router(chatbot_router)