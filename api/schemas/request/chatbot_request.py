from typing import List

from pydantic import Field

from api.schemas.common.base_model import XSSBaseModel


class ChatRequest(XSSBaseModel):
   content : str

class ChatBotWordSetIdsRequest(XSSBaseModel):
   chatbot_wordset_ids: List[str]
   # chatbot_wordset_ids: int = Field(..., alias="chatbotIds")

class ChatBotGenerateRequest(XSSBaseModel):
   description : str