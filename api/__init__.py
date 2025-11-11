from fastapi import APIRouter
from api.routers.chatbot import router as chatbot_router
from api.routers.chatbot_wordset import router as chatbot_wordset_router
from api.routers.chat_history import router as chat_history_router
from api.routers.dit import router as dit_router

api_router = APIRouter()
api_router.include_router(chatbot_router)
api_router.include_router(chatbot_wordset_router)
api_router.include_router(chat_history_router)
api_router.include_router(dit_router)
