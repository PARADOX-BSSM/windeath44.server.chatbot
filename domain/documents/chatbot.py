from typing import List
from beanie import Document, Indexed
from pydantic import field_validator, BaseModel, Field

from exceptions.character_word_set_length_exceeded_exception import CharacterWordSetLengthExceededException


class CharacterWordSet(BaseModel):
    question : str
    answer : str


class ChatBot(Document):
    id : int
    name : str
    character_wordset : List[CharacterWordSet] = Field(default_factory=list)

    @field_validator("character_wordset")
    def validate_character_wordset(cls, v):
        length = len(v)
        if  5 < length:
            raise CharacterWordSetLengthExceededException(length=length)
        return v

    class Settings:
        name = "chatbot"