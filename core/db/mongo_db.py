import motor.motor_asyncio
from beanie import init_beanie
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from domain.documents.chatbot import ChatBot

load_dotenv()

async def init_mongodb(app : FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client['chatbot']
    await init_beanie(database=db, document_models=[ChatBot])
    app.state.mongo_client = client

async def close_mongodb(app: FastAPI):
    app.state.mongo_client.close()