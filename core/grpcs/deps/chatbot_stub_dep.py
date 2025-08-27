import os, grpc

from core.grpcs.client.chatbot_grpc_client import ChatbotGrpcClient
from core.grpcs.gen import get_character_pb2_grpc


async def chatbot_stub_dep():
    target = os.getenv("GRPC_TARGET", "localhost:9090")
    channel = grpc.aio.insecure_channel(target)
    try:
        stub = get_character_pb2_grpc.GetCharacterServiceStub(channel)
        yield ChatbotGrpcClient(stub)
    finally:
        await channel.close()
