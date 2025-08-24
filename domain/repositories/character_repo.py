from typing import List, Optional
from beanie import operators as oper

from api.schemas.request.chatbot_wordset_request import ChatBotWordSetRequest
from domain.documents.character import Character, CharacterWordSet


async def save(character_id : int, character_name : Optional[str] = None, character_wordset : Optional[List[CharacterWordSet]] = None):
    character = Character(
        id = character_id,
        name=character_name,
        character_wordset = character_wordset if character_wordset is not None else [],
    )
    print(f"character wordset : {character.character_wordset}")
    await character.save()


async def find_by_id(character_id) -> Character:
    character = await Character.find_one(Character.id == character_id)
    return character


async def update_wordset(character_id : int, chatbot_wordset_request : ChatBotWordSetRequest):
    character = await find_by_id(character_id)
    await character.update(oper.Set({Character.character_wordset : chatbot_wordset_request.wordset}))