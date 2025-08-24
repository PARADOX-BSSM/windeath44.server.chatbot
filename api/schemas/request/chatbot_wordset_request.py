from typing import List

from pydantic import BaseModel

class ChatBotWordItemRequest(BaseModel):
    question: str
    answer: str

class ChatBotWordSetRequest(BaseModel):
    wordset: List[ChatBotWordItemRequest]

