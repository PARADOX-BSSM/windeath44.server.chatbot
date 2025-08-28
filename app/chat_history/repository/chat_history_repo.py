from app.chat_history.document.chat_history import ChatHistory
from typing import List
from beanie.operators import Eq, LT
from beanie import SortDirection, operators as oper, PydanticObjectId
from bson import ObjectId

async def save(session_id : str, input_text : str, output_text : str):
    chat_history = ChatHistory(session_id=session_id, input_text=input_text, output_text=output_text)
    await chat_history.save()


async def find(session_id: str, size: int) -> List[ChatHistory]:
    chat_history = (
        await ChatHistory.find(Eq(ChatHistory.session_id, session_id))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chat_history


async def find_by_cursor_id(session_id: str, size: int, cursor_id: str) -> List[ChatHistory]:
    chat_history = (
        await ChatHistory.find(
            LT(ChatHistory.id, ObjectId(cursor_id)), Eq(ChatHistory.session_id, session_id)
        )
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chat_history


async def delete_by_session_id(session_id : str):
    await ChatHistory.find(ChatHistory.session_id == session_id).delete()


async def delete_history_by_history_id(history_id : str):
    object_history_id = PydanticObjectId(history_id)
    await ChatHistory.find_one(ChatHistory.id == object_history_id).delete()