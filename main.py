from contextlib import asynccontextmanager

from fastapi import FastAPI
from api import api_router
from core.db.mongo_db import init_mongodb, close_mongodb


@asynccontextmanager
async def lifespan(app : FastAPI):
    await init_mongodb(app)
    yield
    await close_mongodb(app)

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
