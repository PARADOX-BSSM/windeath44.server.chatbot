from typing import List

from beanie.odm.operators.find.comparison import In

from api.schemas.request.chatbot_wordset_request import ChatBotWordIdsRequest
from domain.documents.chatbot_wordset import ChatBotWordSet
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
    chatbots = (
        await ChatBotWordSet.find_all()
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbots

async def find_by_cursor_id(cursor_id : int, size : int) -> List[ChatBotWordSet]:
    chatbots = (
        await ChatBotWordSet.find(oper.LT(ChatBotWordSet.id, cursor_id))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbots


async def find_by_character_id(character_id : int, size : int) -> List[ChatBotWordSet]:
    chatbots = (
        await ChatBotWordSet.find(oper.Eq(ChatBotWordSet.character_id, character_id))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbots


async def find_by_cursor_id_and_character_id(character_id : int, cursor_id : int, size : int) -> List[ChatBotWordSet]:
    chatbots = (
        await ChatBotWordSet.find(oper.LT(ChatBotWordSet.id, cursor_id), oper.Eq(ChatBotWordSet.character_id, character_id))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbots


async def find_chatbot_wordests(chatbot_wordset_ids : List[str]) -> List[ChatBotWordSet]:
    ids = [PydanticObjectId(cid) for cid in chatbot_wordset_ids]

    chatbot_wordsets = await (
        ChatBotWordSet
        .find(In(ChatBotWordSet.id, ids))
        .to_list()
    )
    return chatbot_wordsets