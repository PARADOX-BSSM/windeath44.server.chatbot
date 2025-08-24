import asyncio
from typing import List, Optional
from beanie import operators as oper

from api.schemas.request.chatbot_wordset_request import ChatBotWordSetRequest
from domain.documents.chatbot import ChatBot, CharacterWordSet


async def save(character_id : int, character_name : Optional[str] = None, character_wordset : Optional[List[CharacterWordSet]] = None):
    character = ChatBot(
        id = character_id,
        name=character_name,
        character_wordset = character_wordset if character_wordset is not None else [],
    )
    print(f"character wordset : {character.character_wordset}")
    await character.save()


async def find_by_id(character_id : int) -> ChatBot:
    character = await ChatBot.find_one(ChatBot.id == character_id)
    return character

async def update_wordset(character_id : int, chatbot_wordset_request : ChatBotWordSetRequest):
    character = await find_by_id(character_id)
    await character.update(oper.Set({ChatBot.character_wordset : chatbot_wordset_request.wordset}))


async def exists_by_id(character_id : int) -> bool:
    chatbot = await find_by_id(character_id)
    return bool(chatbot)
