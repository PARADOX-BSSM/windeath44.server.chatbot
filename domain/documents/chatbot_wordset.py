from beanie import Document


class ChatBotWordSet(Document):
    character_id : int
    question : str
    answer : str


    class Settings:
        name = "chat_bot_wordset"