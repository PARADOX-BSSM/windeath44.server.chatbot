from api.schemas.common.response.cursor_response import CursorResponse
from api.schemas.request.chatbot_wordset_request import ChatBotWordIdsRequest
from domain.repositories import chatbot_wordset_repo


async def add(character_id : int, chatbot_wordset_request : ChatBotWordIdsRequest, user_id : str):
    await chatbot_wordset_repo.save(character_id, chatbot_wordset_request, user_id)


async def get_chatbot_wordset(cursor_id : int, size : int) -> CursorResponse:
    chatbot_wordset = await chatbot_wordset_repo.find(size) if cursor_id is None else await chatbot_wordset_repo.find_by_cursor_id(cursor_id, size)
    has_next = len(chatbot_wordset) > size
    return CursorResponse(hasNext=has_next, values=chatbot_wordset)


async def get_chatbot_wordset_by_character(character_id : int, cursor_id : int, size : int) -> CursorResponse:
    chatbot_wordset = await chatbot_wordset_repo.find_by_character_id(character_id, size) if cursor_id is None else await chatbot_wordset_repo.find_by_cursor_id_and_character_id(character_id, cursor_id, size)
    has_next = len(chatbot_wordset) > size
    return CursorResponse(hasNext=has_next, values=chatbot_wordset)
