from api.schemas.common.response.cursor_response import CursorResponse
from app.chat_history.repository import chat_history_repo
from core.sessions import session_id_generator


async def get_chat_histories(chatbot_id : int, cursor_id : str, size : int, user_id : str) -> CursorResponse:
    session_id = await session_id_generator.generate_chat_session_id(chatbot_id=chatbot_id, user_id=user_id)

    chat_histories = (
        await chat_history_repo.find(
            session_id=session_id,
            size=size
        )
        if cursor_id is None else
        await chat_history_repo.find_by_cursor_id(
            session_id=session_id,
            cursor_id=cursor_id,
            size=size
        )
    )
    has_next = len(chat_histories) > size
    return CursorResponse(hasNext=has_next, values=chat_histories)


async def delete_by_session_id(chatbot_id : int, user_id : str):
    session_id = await session_id_generator.generate_chat_session_id(chatbot_id=chatbot_id, user_id=user_id)
    await chat_history_repo.delete_by_session_id(session_id=session_id)


async def delete_by_history_id(history_id : str):
    await chat_history_repo.delete_history_by_history_id(history_id=history_id)