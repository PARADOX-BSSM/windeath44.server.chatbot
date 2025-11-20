from typing import List

from api.schemas.common.base_model import XSSBaseModel

class ChatBotWordIdsRequest(XSSBaseModel):
    question: str
    answer: str

class ChatBotWordSetRequest(XSSBaseModel):
    wordset: List[ChatBotWordIdsRequest]