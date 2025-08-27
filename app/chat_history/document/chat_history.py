
from beanie import Document


class ChatHistory(Document):
    session_id : str
    input_text : str
    output_text :str

    class Settings:
        name = "chat_history"