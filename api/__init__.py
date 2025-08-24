from fastapi import APIRouter
from api.routers.chatbot import router as chatbot_router
from api.routers.chatbot_wordset import router as chatbot_wordset_router

api_router = APIRouter()
api_router.include_router(chatbot_router)
api_router.include_router(chatbot_wordset_router)
