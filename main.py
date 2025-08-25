from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

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
async def global_exception_handler(request : Request, exc: Exception):
    if isinstance(exc, BusinessException):
        print("error:", exc.message)
        print("status code:", exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "status": exc.status_code
            },
        )
    print("error:", str(exc))
    return JSONResponse(status_code=500, content={
                "message": str(exc),
                "status": 500
            })

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
