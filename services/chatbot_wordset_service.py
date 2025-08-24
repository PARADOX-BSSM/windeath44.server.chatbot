from api.schemas.request.chatbot_wordset_request import ChatBotWordSetRequest
from domain.repositories import character_repo


async def modify(character_id : int, chatbot_wordset_request : ChatBotWordSetRequest):
    await character_repo.update_wordset(character_id, chatbot_wordset_request)
