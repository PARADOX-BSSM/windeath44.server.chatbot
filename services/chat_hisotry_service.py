from api.schemas.common.response.cursor_response import CursorResponse
from domain.repositories import chat_hisotry_repo
from sessions import session_id_generator

async def get_chat_histories(chatbot_id : int, cursor_id : str, size : int, user_id : str) -> CursorResponse:
    session_id = await session_id_generator.generate_chat_session_id(chatbot_id=chatbot_id, user_id=user_id)

    chat_histories = (
        await chat_hisotry_repo.find(
            session_id=session_id,
            size=size
        )
        if cursor_id is None else
        await chat_hisotry_repo.find_by_cursor_id(
            session_id=session_id,
            cursor_id=cursor_id,
            size=size
        )
    )
    has_next = len(chat_histories) > size
    return CursorResponse(hasNext=has_next, values=chat_histories)