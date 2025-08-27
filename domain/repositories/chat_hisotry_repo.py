from typing import List

from beanie import SortDirection

from api.schemas.common.response.cursor_response import CursorResponse
from domain.documents.chat_history import ChatHistory
from domain.repositories import chatbot_repo


async def save(session_id : str, input_text : str, output_text : str):
    chat_history = ChatHistory(session_id=session_id, input_text=input_text, output_text=output_text)
    chat_history.save()

async def find(size : int) -> List[ChatHistory]:
    chat_history = (
        await ChatHistory.find_all()
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chat_history
