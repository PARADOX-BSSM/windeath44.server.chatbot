from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from api import api_router
from core.db.mongo_db import init_mongodb, close_mongodb
from exceptions.business_exception import BusinessException


@asynccontextmanager
async def lifespan(app : FastAPI):
    await init_mongodb(app)
    yield
    await close_mongodb(app)

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request : Request, exception: Exception):
        if isinstance(exception, BusinessException):
            print("error : ", exception.message)
            print("status code:", exception.status_code)
            raise HTTPException(status_code=exception.status_code, detail=exception.message)
        print("error : ", str(exception))
        raise HTTPException(status_code=500, detail=str(exception))

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
