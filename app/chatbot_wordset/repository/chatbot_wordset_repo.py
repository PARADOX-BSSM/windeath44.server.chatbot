from typing import List

from beanie.odm.operators.find.comparison import In

from api.schemas.request.chatbot_wordset_request import ChatBotWordIdsRequest
from app.chatbot_wordset.document.chatbot_wordset import ChatBotWordSet
from beanie import operators as oper, SortDirection, PydanticObjectId


async def save(character_id : int, chatbot_wordset_request : ChatBotWordIdsRequest, user_id : str):
    chatbot_wordset = ChatBotWordSet(
        character_id=character_id,
        question= chatbot_wordset_request.question,
        answer = chatbot_wordset_request.answer,
        writer_id=user_id
    )
    await chatbot_wordset.save()


async def find(size : int) -> List[ChatBotWordSet]:
    chatbot_wordsets = (
        await ChatBotWordSet.find_all()
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot_wordsets

async def find_by_cursor_id(cursor_id : int, size : int) -> List[ChatBotWordSet]:
    chatbot_wordsets = (
        await ChatBotWordSet.find(oper.LT(ChatBotWordSet.id, cursor_id))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot_wordsets


async def find_by_character_id(character_id : int, size : int) -> List[ChatBotWordSet]:
    chatbot_wordsets = (
        await ChatBotWordSet.find(oper.Eq(ChatBotWordSet.character_id, character_id))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot_wordsets


async def find_by_cursor_id_and_character_id(character_id : int, cursor_id : int, size : int) -> List[ChatBotWordSet]:
    chatbot_wordsets = (
        await ChatBotWordSet.find(oper.LT(ChatBotWordSet.id, cursor_id), oper.Eq(ChatBotWordSet.character_id, character_id))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot_wordsets


async def find_chatbot_wordests(chatbot_wordset_ids : List[str]) -> List[ChatBotWordSet]:
    ids = [PydanticObjectId(cid) for cid in chatbot_wordset_ids]

    chatbot_wordsets = await (
        ChatBotWordSet
        .find(In(ChatBotWordSet.id, ids))
        .to_list()
    )
    return chatbot_wordsets


async def find_by_id(wordset_id: str) -> ChatBotWordSet:
    """특정 ID로 wordset 조회"""
    return await ChatBotWordSet.get(PydanticObjectId(wordset_id))


async def update_status(wordset_id: str, status: str) -> ChatBotWordSet:
    """wordset의 상태 업데이트"""
    wordset = await find_by_id(wordset_id)
    wordset.status = status
    await wordset.save()
    return wordset



async def delete_by_id(wordset_id: str):
    """wordset 삭제"""
    wordset = await find_by_id(wordset_id)
    await wordset.delete()


async def find_by_status(status: str, size: int) -> List[ChatBotWordSet]:
    """상태별 wordset 조회"""
    chatbot_wordsets = (
        await ChatBotWordSet.find(oper.Eq(ChatBotWordSet.status, status))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot_wordsets


async def find_by_cursor_id_and_status(cursor_id: int, status: str, size: int) -> List[ChatBotWordSet]:
    """커서 ID와 상태로 wordset 조회"""
    chatbot_wordsets = (
        await ChatBotWordSet.find(
            oper.LT(ChatBotWordSet.id, cursor_id),
            oper.Eq(ChatBotWordSet.status, status)
        )
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot_wordsets


async def find_by_character_id_and_status(character_id: int, status: str, size: int) -> List[ChatBotWordSet]:
    """캐릭터 ID와 상태로 wordset 조회"""
    chatbot_wordsets = (
        await ChatBotWordSet.find(
            oper.Eq(ChatBotWordSet.character_id, character_id),
            oper.Eq(ChatBotWordSet.status, status)
        )
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot_wordsets


async def find_by_cursor_id_character_id_and_status(
    character_id: int, cursor_id: int, status: str, size: int
) -> List[ChatBotWordSet]:
    """커서 ID, 캐릭터 ID, 상태로 wordset 조회"""
    chatbot_wordsets = (
        await ChatBotWordSet.find(
            oper.LT(ChatBotWordSet.id, cursor_id),
            oper.Eq(ChatBotWordSet.character_id, character_id),
            oper.Eq(ChatBotWordSet.status, status)
        )
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot_wordsets
