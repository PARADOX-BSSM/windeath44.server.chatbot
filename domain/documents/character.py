from typing import List
from beanie import Document, Indexed
from pydantic import field_validator
from exceptions.character_word_set_length_exceeded_exception import CharacterWordSetLengthExceededException

class Character(Document):
    id : int
    name : str
    character_wordset : 'List[CharacterWordSet]'

    @field_validator("character_wordset")
    def validate_character_wordset(cls, v):
        length = len(v)
        if  5 < length:
            raise CharacterWordSetLengthExceededException(length=length)

    class Settings:
        name = "character"

class CharacterWordSet:
    question : str
    answer : str
