from core.grpcs.gen import user_pb2_grpc, user_pb2


class UserGrpcClient:
    def __init__(self, stub: user_pb2_grpc.UserServiceStub):
        self._stub = stub

    async def get_user_remain_token(self, user_id: str) -> int:
        """
        유저의 남은 토큰 수를 조회합니다.
        
        Args:
            user_id: 조회할 유저의 ID
            
        Returns:
            int: 유저의 남은 토큰 수 (remain_token)
        """
        request = user_pb2.GetUserRemainTokenRequest(user_id=user_id)
        response = await self._stub.getUserRemainToken(request)
        return response.remain_token
