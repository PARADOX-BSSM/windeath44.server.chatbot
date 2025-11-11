import os
import grpc
from dotenv import load_dotenv

from core.grpcs.client.user_grpc_client import UserGrpcClient
from core.grpcs.gen import user_pb2_grpc

load_dotenv()


async def user_stub_dep():
    target = os.getenv("USER_GRPC_TARGET", "localhost:9090")
    channel = grpc.aio.insecure_channel(target)
    try:
        stub = user_pb2_grpc.UserServiceStub(channel)
        yield UserGrpcClient(stub)
    finally:
        await channel.close()
