import motor.motor_asyncio
from beanie import init_beanie
from fastapi import FastAPI

from domain.documents.character import Character

async def init_mongodb(app : FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['chatbot']
    await init_beanie(database=db, document_models=[Character])
    app.state.mongo_client = client

async def close_mongodb(app: FastAPI):
    await app.state.mongo_client.close()