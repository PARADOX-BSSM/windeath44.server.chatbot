from pydantic import BaseModel


class ChatbotResponse(BaseModel):
    answer : str = None
