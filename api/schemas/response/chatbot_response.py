from pydantic import BaseModel


class ChatbotResponse(BaseModel):
    comment : str = None
