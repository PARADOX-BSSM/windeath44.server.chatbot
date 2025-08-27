from typing import List

from pydantic import BaseModel


class ChatResponse(BaseModel):
    answer : str = None


class ContributorResponse(BaseModel):
    contributor_id : str

class ChatBotResponse(BaseModel):
    chatbot_id : int
    name : str = None
    contributor : List[ContributorResponse]
