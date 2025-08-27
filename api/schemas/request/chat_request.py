from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
   content : str

class ChatBotWordSetIdsRequest(BaseModel):
   chatbot_wordset_ids: List[str]
   # chatbot_wordset_ids: int = Field(..., alias="chatbotIds")