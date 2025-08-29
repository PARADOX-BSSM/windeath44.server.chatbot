from typing import List, Optional, Set
from beanie import operators as oper, SortDirection

from app.chatbot.document.chatbot import ChatBot, CharacterWordSet
from app.chatbot.exception.not_found_chatbot_exception import NotFoundChatBotException


async def save(character_id : int, character_name : Optional[str] = None, description : str = None, character_wordset : Optional[List[CharacterWordSet]] = None):
    chatbot = ChatBot(
        id = character_id,
        name=character_name,
        description=description,
        character_wordset= character_wordset if character_wordset is not None else [],
        contributors = [],
        is_open=False
    )
    print(f"character wordset : {chatbot.character_wordset}")
    await chatbot.save()


async def find_by_id(character_id : int) -> ChatBot:
    chatbot = await ChatBot.find_one(ChatBot.id == character_id)
    if chatbot is None:
        raise NotFoundChatBotException(chatbot_id=character_id)
    return chatbot

async def update_wordset(character_id : int, chatbot_wordsets : List[CharacterWordSet], contributors : List[str]):
    character = await find_by_id(character_id)
    await character.update(
        oper.Set({ChatBot.character_wordset : chatbot_wordsets}),
        oper.Push({ChatBot.contributors : {"$each" : contributors}}),
    )


async def exists_by_id(character_id : int) -> bool:
    chatbot = await ChatBot.find_one(ChatBot.id == character_id)
    return bool(chatbot)


async def find(is_open : bool, size : int) -> List[ChatBot]:
    chatbot = (
        await ChatBot.find(ChatBot.is_open == is_open)
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbot

async def find_by_cursor_id(is_open : bool, cursor_id : int, size : int) -> List[ChatBot]:
    chatbots = (
        await ChatBot.find(
            ChatBot.is_open == is_open,
            oper.LT(ChatBot.id, cursor_id)
        )
        .sort(("_id", SortDirection.DESCENDING))
        .limit(size + 1)
        .to_list()
    )
    return chatbots


async def toggle_open(chatbot_id : int) -> bool:
    chatbot = await find_by_id(chatbot_id)
    chatbot.is_open = not chatbot.is_open
    await chatbot.save()
    return chatbot.is_open