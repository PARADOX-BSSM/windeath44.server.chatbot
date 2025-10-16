import os
import grpc

from core.grpcs.client.user_grpc_client import UserGrpcClient
from core.grpcs.gen import user_pb2_grpc


async def user_stub_dep():
    """
    FastAPI dependency로 사용할 User gRPC 클라이언트를 제공합니다.
    
    환경변수 USER_GRPC_TARGET으로 gRPC 서버 주소를 설정할 수 있습니다.
    기본값은 localhost:9090입니다.
    
    Usage:
        @app.get("/users/{user_id}/token")
        async def get_user_token(
            user_id: str,
            user_client: UserGrpcClient = Depends(user_stub_dep)
        ):
            remain_token = await user_client.get_user_remain_token(user_id)
            return {"remain_token": remain_token}
    """
    target = os.getenv("USER_GRPC_TARGET", "localhost:9090")
    channel = grpc.aio.insecure_channel(target)
    try:
        stub = user_pb2_grpc.UserServiceStub(channel)
        yield UserGrpcClient(stub)
    finally:
        await channel.close()
