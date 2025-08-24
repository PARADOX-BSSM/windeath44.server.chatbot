from typing import List, Optional

from domain.documents.character import Character, CharacterWordSet


async def save(character_id : int, character_name : Optional[str] = None, character_wordset : Optional[List[CharacterWordSet]] = None):
    character = Character(
        id = character_id,
        name=character_name,
        character_wordset = character_wordset or []
    )
    await character.save()


async def find_by_id(character_id) -> Character:
    character = await Character.find_one(Character.id == character_id)
    return character