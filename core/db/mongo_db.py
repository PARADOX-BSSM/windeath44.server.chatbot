import motor.motor_asyncio
from beanie import init_beanie
from fastapi import FastAPI
from dotenv import load_dotenv
import os

from app.chat_history.document.chat_history import ChatHistory
from app.chatbot.document.chatbot import ChatBot
from app.chatbot_wordset.document.chatbot_wordset import ChatBotWordSet

load_dotenv()

async def init_mongodb(app : FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client['chatbot']
    await init_beanie(database=db, document_models=[ChatBot, ChatBotWordSet, ChatHistory])
    app.state.mongo_client = client

async def close_mongodb(app: FastAPI):
    app.state.mongo_client.close()