from pydantic import BaseModel

class ChatBotGeneratedResponse(BaseModel):
    generated : bool = False