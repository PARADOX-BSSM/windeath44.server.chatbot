from typing import List

from pydantic import BaseModel

class ChatBotWordIdsRequest(BaseModel):
    question: str
    answer: str

class ChatBotWordSetRequest(BaseModel):
    wordset: List[ChatBotWordIdsRequest]