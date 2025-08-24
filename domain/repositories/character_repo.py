from typing import List, Optional

from domain.documents.character import Character, CharacterWordSet


async def save(character_name : Optional[str] = None, character_wordset : Optional[List[CharacterWordSet]] = None):
    character = Character(
        name=character_name,
        character_wordset = character_wordset or []
    )
    await character.save()