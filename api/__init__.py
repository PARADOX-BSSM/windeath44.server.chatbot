from fastapi import APIRouter
from api.routers.chatbot import router as chatbot_router

api_router = APIRouter(prefix="/api")
api_router.include_router(chatbot_router)