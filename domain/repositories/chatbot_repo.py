import asyncio
from typing import List, Optional
from beanie import operators as oper, SortDirection


from api.schemas.request.chatbot_wordset_request import ChatBotWordSetRequest
from domain.documents.chatbot import ChatBot, CharacterWordSet
from domain.documents.chatbot_wordset import ChatBotWordSet
from exceptions.not_found_chatbot_exception import NotFoundChatBotException


async def save(character_id : int, character_name : Optional[str] = None, character_wordset : Optional[List[CharacterWordSet]] = None):
    character = ChatBot(
        id = character_id,
        name=character_name,
        character_wordset = character_wordset if character_wordset is not None else [],
    )
    print(f"character wordset : {character.character_wordset}")
    await character.save()


async def find_by_id(character_id : int) -> ChatBot:
    chatbot = await ChatBot.find_one(ChatBot.id == character_id)
    if chatbot is None:
        raise NotFoundChatBotException(chatbot_id=character_id)
    return chatbot

async def update_wordset(character_id : int, chatbot_wordsets : List[CharacterWordSet]):
    character = await find_by_id(character_id)
    await character.update(oper.Set({ChatBot.character_wordset : chatbot_wordsets}))


async def exists_by_id(character_id : int) -> bool:
    chatbot = await find_by_id(character_id)
    return bool(chatbot)


async def find(size : int) -> List[ChatBot]:
    chatBotWordSet = (
        await ChatBot.find_all()
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatBotWordSet

async def find_by_cursor_id(cursor_id : int, size : int) -> List[ChatBot]:
    chatbots = (
        await ChatBot.find(oper.LT(ChatBot.id, cursor_id))
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbots