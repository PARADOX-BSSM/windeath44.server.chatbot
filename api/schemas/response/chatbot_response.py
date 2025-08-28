from typing import List, Set

from pydantic import BaseModel


class ChatResponse(BaseModel):
    answer : str = None

class ChatBotResponse(BaseModel):
    chatbot_id : int
    name : str = None
    description : str
    contributor : List[str]

class CharacterWordSet(BaseModel):
    question : str
    answer : str
    contributor : str # user_id

class ChatBotDetailsResponse(ChatBotResponse):
    chatbot_wordset : List[CharacterWordSet]