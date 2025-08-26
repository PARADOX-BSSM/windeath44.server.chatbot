
from adapter.grpc.gen import get_character_pb2_grpc, get_character_pb2

class ChatbotGrpcClient:
    def __init__(self, stub: get_character_pb2_grpc.GetCharacterServiceStub):
        self._stub = stub

    async def get_character(self, character_id: int) -> get_character_pb2.GetCharacterResponse:
        request = get_character_pb2.GetCharacterRequest(characterId=character_id)
        character = await self._stub.getCharacter(request)
        return character

