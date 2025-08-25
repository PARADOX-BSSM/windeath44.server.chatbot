from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
   content : str

class ChatBotIdsRequest(BaseModel):
   chatbot_ids: List[int]
   # chatbot_ids: int = Field(..., alias="chatbotIds")