from beanie import Document


class ChatBotWordSet(Document):
    character_id : int
    question : str
    answer : str
    writer_id : str

    class Settings:
        name = "chat_bot_wordset"